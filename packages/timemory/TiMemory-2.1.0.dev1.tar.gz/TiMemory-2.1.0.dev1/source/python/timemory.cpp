// MIT License
//
// Copyright (c) 2018, The Regents of the University of California, 
// through Lawrence Berkeley National Laboratory (subject to receipt of any 
// required approvals from the U.S. Dept. of Energy).  All rights reserved.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//

#include <future>
#include <chrono>
#include <functional>
#include <mutex>
#include <thread>
#include <atomic>
#include <iostream>
#include <cstdint>
#include <sstream>
#include <map>
#include <string>
#include <vector>
#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <pybind11/numpy.h>
#include <pybind11/iostream.h>
#include <pybind11/eval.h>
#include <pybind11/embed.h>
#include <pybind11/cast.h>
#include <pybind11/pytypes.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
using namespace std::placeholders;  // for _1, _2, _3...
using namespace py::literals;

#include "timemory/macros.hpp"
#include "timemory/manager.hpp"
#include "timemory/timer.hpp"
#include "timemory/rss.hpp"
#include "timemory/auto_timer.hpp"
#include "timemory/signal_detection.hpp"
#include "timemory/rss.hpp"
#include "timemory/mpi.hpp"
#include "timemory/formatters.hpp"

typedef tim::manager                            manager_t;
typedef tim::timer                              tim_timer_t;
typedef tim::auto_timer                         auto_timer_t;
typedef tim::rss::usage                         rss_usage_t;
typedef tim::rss::usage_delta                   rss_delta_t;
typedef tim::sys_signal                         sys_signal_t;
typedef tim::signal_settings                    signal_settings_t;
typedef signal_settings_t::signal_set_t         signal_set_t;
typedef tim::format::timer                      timer_format_t;
typedef tim::format::rss                        rss_format_t;
typedef tim::format::base_formatter::unit_type  unit_type;

typedef py::array_t<double, py::array::c_style | py::array::forcecast> farray_t;

//============================================================================//

class manager_wrapper
{
public:
    manager_wrapper()
    : m_manager(manager_t::instance())
    { }

    ~manager_wrapper()
    { }

    // ensures thread-local version is called
    manager_t* get() { return manager_t::instance(); }

protected:
    manager_t* m_manager;
};

//============================================================================//

class auto_timer_decorator
{
public:
    auto_timer_decorator(auto_timer_t* _ptr = nullptr)
    : m_ptr(_ptr)
    {
        if(m_ptr)
            m_ptr->local_timer().summation_timer()->format()->align_width(true);
    }

    ~auto_timer_decorator()
    {
        delete m_ptr;
    }

    auto_timer_decorator& operator=(auto_timer_t* _ptr)
    {
        if(m_ptr)
            delete m_ptr;
        m_ptr = _ptr;
        m_ptr->local_timer().summation_timer()->format()->align_width(true);
        return *this;
    }

private:
    auto_timer_t* m_ptr;
};

//============================================================================//

#if _PYTHON_MAJOR_VERSION > 2
#   define PYOBJECT_SELF
#   define PYOBJECT_SELF_PARAM
#else
#   define PYOBJECT_SELF py::object,
#   define PYOBJECT_SELF_PARAM py::object
#endif

//============================================================================//

//============================================================================//
//  Python wrappers
//============================================================================//

PYBIND11_MODULE(timemory, tim)
{
    //------------------------------------------------------------------------//
    py::add_ostream_redirect(tim, "ostream_redirect");
    //------------------------------------------------------------------------//
    auto man_init = [&] () { return new manager_wrapper(); };
    //------------------------------------------------------------------------//
    auto get_line = [] (int nback = 1)
    {
        auto locals = py::dict("back"_a = nback);
        py::exec(R"(
                 import sys
                 result = int(sys._getframe(back).f_lineno)
                 )", py::globals(), locals);
        auto ret = locals["result"].cast<int>();
        return ret;
    };
    //------------------------------------------------------------------------//
    auto get_func = [] (int nback = 1)
    {
        auto locals = py::dict("back"_a = nback);
        py::exec(R"(
                 import sys
                 result = ("{}".format(sys._getframe(back).f_code.co_name))
                 )", py::globals(), locals);
        auto ret = locals["result"].cast<std::string>();
        return ret;
    };
    //------------------------------------------------------------------------//
    auto get_file = [] (int nback = 2, bool only_basename = true,
                    bool use_dirname = false, bool noquotes = false)
    {
        auto locals = py::dict("back"_a = nback,
                               "only_basename"_a = only_basename,
                               "use_dirname"_a = use_dirname,
                               "noquotes"_a = noquotes);
        py::exec(R"(
                 import sys
                 import os
                 from os.path import dirname
                 from os.path import basename
                 from os.path import join

                 def get_fcode(back):
                     fname = '<module'
                     try:
                         fname = sys._getframe(back).f_code.co_filename
                     except:
                         fname = '<module>'
                     return fname

                 result = None
                 if only_basename:
                     if use_dirname:
                         result = ("{}".format(join(basename(dirname(get_fcode(back))),
                           basename(get_fcode(back)))))
                     else:
                         result = ("{}".format(basename(get_fcode(back))))
                 else:
                     result = ("{}".format(get_fcode(back)))

                 if noquotes is False:
                     result = ("'{}'".format(result))
                 )", py::globals(), locals);
        auto ret = locals["result"].cast<std::string>();
        return ret;
    };
    //------------------------------------------------------------------------//
    auto set_timer_default_format = [=] (std::string format)
    {
        // update C++
        tim::format::timer::default_format(format);
        return format;
    };
    //------------------------------------------------------------------------//
    auto get_timer_default_format = [=] ()
    {
        // in case changed in python, update C++
        return tim::format::timer::default_format();
    };
    //------------------------------------------------------------------------//
    auto timer_init = [=] (std::string prefix = "", std::string format = "")
    {
        if(prefix.empty())
        {
            std::stringstream keyss;
            keyss << get_func(1) << "@" << get_file(2) << ":" << get_line(1);
            prefix = keyss.str();
        }

        if(format.empty())
            format = get_timer_default_format();

        return new tim_timer_t(prefix, format);
    };
    //------------------------------------------------------------------------//
    auto auto_timer_init = [=] (const std::string& key = "",
                                bool report_at_exit = false,
                                int nback = 1,
                                bool added_args = false)
    {
        std::stringstream keyss;
        keyss << get_func(nback);

        if(added_args)
            keyss << key;
        else if(key != "" && key[0] != '@' && !added_args)
            keyss << "@";

        if(key != "" && !added_args)
            keyss << key;
        else
        {
            keyss << "@";
            keyss << get_file(nback+1);
            keyss << ":";
            keyss << get_line(nback);
        }
        auto op_line = get_line();
        return new auto_timer_t(keyss.str(), op_line, "pyc", report_at_exit);
    };
    //------------------------------------------------------------------------//
    /*
    auto auto_timer_from_timer = [=] (py::object _pytimer,
                                      bool report_at_exit)
    {
        tim_timer_t* _timer = _pytimer.cast<tim_timer_t*>();
        auto op_line = get_line();
        return new auto_timer_t(*_timer, op_line, "pyc", report_at_exit);
    };
    */
    //------------------------------------------------------------------------//
    auto timer_decorator_init = [=] (const std::string& func,
                                     const std::string& file,
                                     int line,
                                     const std::string& key,
                                     bool added_args,
                                     bool report_at_exit)
    {
        auto_timer_decorator* _ptr = new auto_timer_decorator();
        if(!auto_timer_t::alloc_next())
            return _ptr;

        std::stringstream keyss;
        keyss << func;

        // add arguments to end of function
        if(added_args)
            keyss << key;
        else if(key != "" && key[0] != '@' && !added_args)
            keyss << "@";

        if(key != "" && !added_args)
            keyss << key;
        else
        {
            keyss << "@";
            keyss << file;
            keyss << ":";
            keyss << line;
        }
        return &(*_ptr = new auto_timer_t(keyss.str(), line, "pyc", report_at_exit));
    };
    //------------------------------------------------------------------------//
    auto rss_usage_init = [=] (std::string prefix = "",
                               bool record = false,
                               std::string format = "")
    {
        rss_format_t _fmt(prefix);
        if(format.length() > 0)
            _fmt.format(format);
        rss_usage_t* _rss = (record)
                            ? new rss_usage_t(0, _fmt) : new rss_usage_t(_fmt);
        return _rss;
    };
    //------------------------------------------------------------------------//
    auto rss_delta_init = [=] (std::string prefix = "",
                               std::string format = "")
    {
        rss_format_t _fmt = tim::format::timer::default_rss_format();
        _fmt.prefix(prefix);
        if(format.length() > 0)
            _fmt.format(format);
        rss_delta_t* _rss = new rss_delta_t(_fmt);
        _rss->init();
        return _rss;
    };
    //------------------------------------------------------------------------//
    auto signal_list_to_set = [=] (py::list signal_list) -> signal_set_t
    {
        signal_set_t signal_set;
        for(auto itr : signal_list)
            signal_set.insert(itr.cast<sys_signal_t>());
        return signal_set;
    };
    //------------------------------------------------------------------------//
    auto get_default_signal_set = [=] () -> signal_set_t
    {
        return tim::signal_settings::enabled();
    };
    //------------------------------------------------------------------------//
    auto enable_signal_detection = [=] (py::list signal_list = py::list())
    {
        auto _sig_set = (signal_list.size() == 0)
                        ? get_default_signal_set()
                        : signal_list_to_set(signal_list);
        tim::enable_signal_detection(_sig_set);
    };
    //------------------------------------------------------------------------//
    auto disable_signal_detection = [=] ()
    {
        tim::disable_signal_detection();
    };
    //------------------------------------------------------------------------//
    auto timing_fmt_init = [=] (const std::string& prefix = "",
                           const std::string& format = timer_format_t::default_format(),
                           unit_type unit = timer_format_t::default_unit(),
                           py::object rss_format = py::none(),
                           bool align_width = false)
    {
        rss_format_t _rss_format = tim::format::timer::default_rss_format();
        if(!rss_format.is_none())
            _rss_format = *rss_format.cast<rss_format_t*>();

        return new timer_format_t(prefix, format, unit, _rss_format, align_width);
    };
    //------------------------------------------------------------------------//
    auto memory_fmt_init = [=] (const std::string& prefix = "",
                           const std::string& format = rss_format_t::default_format(),
                           unit_type unit = rss_format_t::default_unit(),
                           bool align_width = false)
    {
        return new rss_format_t(prefix, format, unit, align_width);
    };
    //------------------------------------------------------------------------//


    //========================================================================//
    //
    //                  MAIN timemory MODULE (part 1)
    //
    //========================================================================//
    tim.def("LINE",
            get_line,
            "Function that emulates __LINE__ macro",
            py::arg("nback") = 1);
    //------------------------------------------------------------------------//
    tim.def("FUNC",
            get_func,
            "Function that emulates __FUNC__ macro",
            py::arg("nback") = 1);
    //------------------------------------------------------------------------//
    tim.def("FILE",
            get_file,
            "Function that emulates __FILE__ macro",
            py::arg("nback") = 2,
            py::arg("basename_only") = true,
            py::arg("use_dirname") = false,
            py::arg("noquotes") = false);
    //------------------------------------------------------------------------//
    tim.def("set_max_depth",
            [=] (int32_t ndepth)
            { manager_t::instance()->set_max_depth(ndepth); },
            "Max depth of auto-timers");
    //------------------------------------------------------------------------//
    tim.def("get_max_depth",
            [=] ()
            { return manager_t::instance()->get_max_depth(); },
            "Max depth of auto-timers");
    //------------------------------------------------------------------------//
    tim.def("toggle",
            [=] (bool timers_on)
            { manager_t::instance()->enable(timers_on); },
            "Enable/disable auto-timers",
            py::arg("timers_on") = true);
    //------------------------------------------------------------------------//
    tim.def("enabled",
            [=] ()
            { return manager_t::instance()->is_enabled(); },
            "Return if the auto-timers are enabled or disabled");
    //------------------------------------------------------------------------//
    tim.def("enable_signal_detection",
            enable_signal_detection,
            "Enable signal detection",
            py::arg("signal_list") = py::list());
    //------------------------------------------------------------------------//
    tim.def("disable_signal_detection",
            disable_signal_detection,
            "Enable signal detection");
    //------------------------------------------------------------------------//
    tim.def("set_default_format",
            set_timer_default_format,
            "Set the default format of the timers");
    //------------------------------------------------------------------------//
    tim.def("get_default_format",
            get_timer_default_format,
            "Get the default format of the timers");
    //------------------------------------------------------------------------//
    tim.def("has_mpi_support",
            [=] ()
            { return tim::has_mpi_support(); },
            "Return if the TiMemory library has MPI support");
    //------------------------------------------------------------------------//
    tim.def("get_overhead_report",
            [=] ()
            {
                std::stringstream _ss;
                manager_t::instance()->write_overhead(_ss);
                return _ss.str();
            },
            "Get TiMemory overhead as string");
    //------------------------------------------------------------------------//


    //========================================================================//
    //
    //      Units submodule
    //
    //========================================================================//
    py::module units = tim.def_submodule("units",
                                         "units for timing and memory");

    units.attr("psec") = tim::units::psec;
    units.attr("nsec") = tim::units::nsec;
    units.attr("usec") = tim::units::usec;
    units.attr("msec") = tim::units::msec;
    units.attr("csec") = tim::units::csec;
    units.attr("dsec") = tim::units::dsec;
    units.attr("sec") = tim::units::sec;
    units.attr("byte") = tim::units::byte;
    units.attr("kilobyte") = tim::units::kilobyte;
    units.attr("megabyte") = tim::units::megabyte;
    units.attr("gigabyte") = tim::units::gigabyte;
    units.attr("terabyte") = tim::units::terabyte;
    units.attr("petabyte") = tim::units::petabyte;

    //========================================================================//
    //
    //      Format submodule
    //
    //========================================================================//
    py::module fmt = tim.def_submodule("format",
                                       "timing and memory format submodule");

    //------------------------------------------------------------------------//
    //      format.timer
    //------------------------------------------------------------------------//
    py::class_<tim::format::timer> timing_fmt(fmt, "timer");

    timing_fmt.def(py::init(timing_fmt_init),
                   "Initialize timing formatter",
                   py::return_value_policy::take_ownership,
                   py::arg("prefix") = "",
                   py::arg("format") = timer_format_t::default_format(),
                   py::arg("unit") = timer_format_t::default_unit(),
                   py::arg("rss_format") = py::none(),
                   py::arg("align_width") = false);

    timing_fmt.def("set_default",
                   [=] (PYOBJECT_SELF py::object _val)
                   {
                       timer_format_t* _fmt = _val.cast<timer_format_t*>();
                       timer_format_t::set_default(*_fmt);
                   },
                   "Set the default timer format");
    timing_fmt.def("get_default",
                   [=] (PYOBJECT_SELF_PARAM)
                   {
                       timer_format_t _fmt = timer_format_t::get_default();
                       return new timer_format_t(_fmt);
                   },
                   "Get the default timer format");
    timing_fmt.def("set_default_format",
                   [=] (PYOBJECT_SELF std::string _val)
                   { timer_format_t::default_format(_val); },
                   "Set the default timer format");
    timing_fmt.def("set_default_rss_format",
                   [=] (PYOBJECT_SELF py::object _val)
                   {
                       try
                       {
                           rss_format_t* _rss = _val.cast<rss_format_t*>();
                           timer_format_t::default_rss_format(*_rss);
                       }
                       catch(...)
                       {
                           std::string _fmt = _val.cast<std::string>();
                           auto _rss = timer_format_t::default_rss_format();
                           _rss.format(_fmt);
                           timer_format_t::default_rss_format(_rss);
                       }
                   },
                   "Set the default timer RSS format");
    timing_fmt.def("set_default_precision",
                   [=] (PYOBJECT_SELF const int16_t& _prec)
                   { timer_format_t::default_precision(_prec); },
                   "Set the default timer precision");
    timing_fmt.def("set_default_unit",
                   [=] (PYOBJECT_SELF const int64_t& _unit)
                   { timer_format_t::default_unit(_unit); },
                   "Set the default timer units");
    timing_fmt.def("set_default_width",
                   [=] (PYOBJECT_SELF const int16_t& _w)
                   { timer_format_t::default_width(_w); },
                   "Set the default timer field width");

    timing_fmt.def("copy_from",
                   [=] (py::object self, py::object rhs)
                   {
                       timer_format_t* _self = self.cast<timer_format_t*>();
                       timer_format_t* _rhs = rhs.cast<timer_format_t*>();
                       _self->copy_from(_rhs);
                       return self;
                   },
                   "Copy for format, precision, unit, width, etc. from another format");
    timing_fmt.def("set_format",
                   [=] (py::object obj, std::string _val)
                   { obj.cast<timer_format_t*>()->format(_val); },
                   "Set the timer format");
    timing_fmt.def("set_rss_format",
                   [=] (py::object obj, py::object _val)
                   {
                       rss_format_t* _rss = _val.cast<rss_format_t*>();
                       obj.cast<timer_format_t*>()->rss_format(*_rss);
                   },
                   "Set the timer RSS format");
    timing_fmt.def("set_precision",
                   [=] (py::object obj, const int16_t& _prec)
                   { obj.cast<timer_format_t*>()->precision(_prec); },
                   "Set the timer precision");
    timing_fmt.def("set_unit",
                   [=] (py::object obj, const int64_t& _unit)
                   { obj.cast<timer_format_t*>()->unit(_unit); },
                   "Set the timer units");
    timing_fmt.def("set_width",
                   [=] (py::object obj, const int16_t& _w)
                   { obj.cast<timer_format_t*>()->width(_w); },
                   "Set the timer field width");
    timing_fmt.def("set_use_align_width",
                   [=] (py::object obj, bool _val)
                   { obj.cast<timer_format_t*>()->align_width(_val); },
                   "Set the timer to use the alignment width");
    timing_fmt.def("set_prefix",
                   [=] (py::object self, std::string prefix)
                   {
                       timer_format_t* _self = self.cast<timer_format_t*>();
                       _self->prefix(prefix);
                   },
                   "Set the prefix of timer format");
    timing_fmt.def("set_suffix",
                   [=] (py::object self, std::string suffix)
                   {
                       timer_format_t* _self = self.cast<timer_format_t*>();
                       _self->suffix(suffix);
                   },
                   "Set the suffix of timer format");

    //------------------------------------------------------------------------//
    //      format.rss
    //------------------------------------------------------------------------//
    py::class_<tim::format::rss> memory_fmt(fmt, "rss");

    memory_fmt.def(py::init(memory_fmt_init),
                   "Initialize memory formatter",
                   py::return_value_policy::take_ownership,
                   py::arg("prefix") = "",
                   py::arg("format") = rss_format_t::default_format(),
                   py::arg("unit") = rss_format_t::default_unit(),
                   py::arg("align_width") = false);

    memory_fmt.def("set_default",
                   [=] (PYOBJECT_SELF py::object _val)
                   {
                       rss_format_t* _fmt = _val.cast<rss_format_t*>();
                       rss_format_t::set_default(*_fmt);
                   },
                   "Set the default RSS format");
    memory_fmt.def("get_default",
                   [=] (PYOBJECT_SELF_PARAM)
                   {
                       rss_format_t _fmt = rss_format_t::get_default();
                       return new rss_format_t(_fmt);
                   },
                   "Get the default RSS format");
    memory_fmt.def("set_default_format",
                   [=] (PYOBJECT_SELF std::string _val)
                   { rss_format_t::default_format(_val); },
                   "Set the default RSS format");
    memory_fmt.def("set_default_precision",
                   [=] (PYOBJECT_SELF const int16_t& _prec)
                   { rss_format_t::default_precision(_prec); },
                   "Set the default RSS precision");
    memory_fmt.def("set_default_unit",
                   [=] (PYOBJECT_SELF const int64_t& _unit)
                   { rss_format_t::default_unit(_unit); },
                   "Set the default RSS units");
    memory_fmt.def("set_default_width",
                   [=] (PYOBJECT_SELF const int16_t& _w)
                   { rss_format_t::default_width(_w); },
                   "Set the default RSS field width");

    memory_fmt.def("copy_from",
                   [=] (py::object self, py::object rhs)
                   {
                       rss_format_t* _self = self.cast<rss_format_t*>();
                       rss_format_t* _rhs = rhs.cast<rss_format_t*>();
                       _self->copy_from(_rhs);
                       return self;
                   },
                   "Copy for format, precision, unit, width, etc. from another format");
    memory_fmt.def("set_format",
                   [=] (py::object obj, std::string _val)
                   { obj.cast<rss_format_t*>()->format(_val); },
                   "Set the RSS format");
    memory_fmt.def("set_precision",
                   [=] (py::object obj, const int16_t& _prec)
                   { obj.cast<rss_format_t*>()->precision(_prec); },
                   "Set the RSS precision");
    memory_fmt.def("set_unit",
                   [=] (py::object obj, const int64_t& _unit)
                   { obj.cast<rss_format_t*>()->unit(_unit); },
                   "Set the RSS units");
    memory_fmt.def("set_width",
                   [=] (py::object obj, const int16_t& _w)
                   { obj.cast<rss_format_t*>()->width(_w); },
                   "Set the RSS field width");
    memory_fmt.def("set_use_align_width",
                   [=] (py::object obj, bool _val)
                   { obj.cast<rss_format_t*>()->align_width(_val); },
                   "Set the RSS to use the alignment width");
    memory_fmt.def("set_prefix",
                   [=] (py::object self, std::string prefix)
                   {
                       rss_format_t* _self = self.cast<rss_format_t*>();
                       _self->prefix(prefix);
                   },
                   "Set the prefix of RSS format");
    memory_fmt.def("set_suffix",
                   [=] (py::object self, std::string suffix)
                   {
                       rss_format_t* _self = self.cast<rss_format_t*>();
                       _self->suffix(suffix);
                   },
                   "Set the suffix of RSS format");

    //------------------------------------------------------------------------//
    //  Class declarations
    //------------------------------------------------------------------------//
    py::class_<manager_wrapper> man(tim, "manager");
    //py::class_<manager_wrapper, std::unique_ptr<manager_wrapper, py::nodelete>> man(tim, "manager");
    py::class_<tim_timer_t> timer(tim, "timer");
    py::class_<auto_timer_t> auto_timer(tim, "auto_timer");
    py::class_<auto_timer_decorator> timer_decorator(tim, "timer_decorator");
    py::class_<rss_usage_t> rss_usage(tim, "rss_usage");
    py::class_<rss_delta_t> rss_delta(tim, "rss_delta");


    //========================================================================//
    //
    //                          TIMER
    //
    //========================================================================//
    timer.def(py::init(timer_init),
              "Initialization",
              py::return_value_policy::take_ownership,
              py::arg("prefix") = "", py::arg("format") = "");
    //------------------------------------------------------------------------//
    /*
    timer.def("as_auto_timer",
              [=] (py::object timer, bool report_at_exit = false)
              { return auto_timer_from_timer(timer, report_at_exit); },
              "Create auto-timer from timer",
              py::arg("report_at_exit") = false,
              py::return_value_policy::take_ownership);
    */
    //------------------------------------------------------------------------//
    timer.def("real_elapsed",
              [=] (py::object timer)
              { return timer.cast<tim_timer_t*>()->real_elapsed(); },
              "Elapsed wall clock");
    //------------------------------------------------------------------------//
    timer.def("sys_elapsed",
              [=] (py::object timer)
              { return timer.cast<tim_timer_t*>()->system_elapsed(); },
              "Elapsed system clock");
    //------------------------------------------------------------------------//
    timer.def("user_elapsed",
              [=] (py::object timer)
              { return timer.cast<tim_timer_t*>()->user_elapsed(); },
              "Elapsed user time");
    //------------------------------------------------------------------------//
    timer.def("start",
              [=] (py::object timer)
              { timer.cast<tim_timer_t*>()->start(); },
              "Start timer");
    //------------------------------------------------------------------------//
    timer.def("stop",
              [=] (py::object timer)
              { timer.cast<tim_timer_t*>()->stop(); },
              "Stop timer");
    //------------------------------------------------------------------------//
    timer.def("report",
              [=] (py::object timer, bool ign_cutoff = true)
              { timer.cast<tim_timer_t*>()->print(ign_cutoff); },
              "Report timer",
              py::arg("ign_cutoff") = true);
    //------------------------------------------------------------------------//
    timer.def("__str__",
              [=] (py::object timer, bool ign_cutoff = true)
              { return timer.cast<tim_timer_t*>()->as_string(ign_cutoff); },
              "Stringify timer",
              py::arg("ign_cutoff") = true);
    //------------------------------------------------------------------------//
    timer.def("__iadd__",
             [=] (py::object timer, py::object _rss)
             {
                 *(timer.cast<tim_timer_t*>()) +=
                         *(_rss.cast<rss_usage_t*>());
                 return timer;
             },
             "Add RSS measurement");
    //------------------------------------------------------------------------//
    timer.def("__isub__",
             [=] (py::object timer, py::object _rss)
             {
                 *(timer.cast<tim_timer_t*>()) -=
                         *(_rss.cast<rss_usage_t*>());
                 return timer;
             },
             "Subtract RSS measurement");
    //------------------------------------------------------------------------//
    timer.def("get_format",
              [=] (py::object self)
              {
                  tim_timer_t* _self = self.cast<tim_timer_t*>();
                  auto _fmt = _self->format();
                  if(!_fmt.get())
                  {
                      _self->set_format(timer_format_t());
                      _fmt = _self->format();
                  }
                  return _fmt.get();
              },
              "Set the format of the timer",
              py::return_value_policy::reference_internal);
    //------------------------------------------------------------------------//
    timer.def("set_format",
              [=] (py::object timer, py::object fmt)
              {
                  tim_timer_t* _timer = timer.cast<tim_timer_t*>();
                  timer_format_t* _fmt = fmt.cast<timer_format_t*>();
                  _timer->set_format(*_fmt);
              },
              "Set the format of the timer");
    //------------------------------------------------------------------------//


    //========================================================================//
    //
    //                          TIMING MANAGER
    //
    //========================================================================//
    man.attr("reported_files") = py::list();
    //------------------------------------------------------------------------//
    man.attr("serialized_files") = py::list();
    //------------------------------------------------------------------------//
    man.def(py::init<>(man_init), "Initialization",
             py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    man.def("report",
             [=] (py::object man, bool ign_cutoff = false, bool serialize = false,
                  std::string serial_filename = "")
             {
                 auto locals = py::dict();
                 py::exec(R"(
                          import os
                          import timemory.options as options

                          repfnm = options.report_filename
                          serfnm = options.serial_filename
                          do_ret = options.report_file
                          do_ser = options.serial_file
                          outdir = options.output_dir
                          options.ensure_directory_exists('{}/test.txt'.format(outdir))

                          # absolute paths
                          absdir = os.path.abspath(outdir)

                          if outdir in repfnm:
                              repabs = os.path.abspath(repfnm)
                          else:
                              repabs = os.path.join(absdir, repfnm)

                          if outdir in serfnm:
                              serabs = os.path.abspath(serfnm)
                          else:
                              serabs = os.path.join(absdir, serfnm)
                          )", py::globals(), locals);

                 auto outdir = locals["outdir"].cast<std::string>();
                 auto repfnm = locals["repfnm"].cast<std::string>();
                 auto serfnm = locals["serfnm"].cast<std::string>();
                 auto do_rep = locals["do_ret"].cast<bool>();
                 auto do_ser = locals["do_ser"].cast<bool>();
                 auto repabs = locals["repabs"].cast<std::string>();
                 auto serabs = locals["serabs"].cast<std::string>();

                 if(repfnm.find(outdir) != 0)
                     repfnm = outdir + "/" + repfnm;

                 if(serfnm.find(outdir) != 0)
                     serfnm = outdir + "/" + serfnm;

                 manager_t* _man
                         = man.cast<manager_wrapper*>()->get();

                 // set the output stream
                 if(do_rep)
                 {
                     std::cout << "Outputting manager to '" << repfnm
                               << "'..." << std::endl;
                     _man->set_output_stream(repfnm);

                     man.attr("reported_files").cast<py::list>().append(repabs);
                 }

                 // report ASCII output
                 _man->report(ign_cutoff);

                 // handle the serialization
                 if(!do_ser && serialize)
                 {
                     do_ser = true;
                     if(!serial_filename.empty())
                         serfnm = serial_filename;
                     else if(serfnm.empty())
                         serfnm = "output.json";
                 }

                 if(do_ser && manager_t::instance()->size() > 0)
                 {
                     std::cout << "Serializing manager to '" << serfnm
                               << "'..." << std::endl;
                     _man->write_serialization(serfnm);
                     man.attr("serialized_files").cast<py::list>().append(serabs);
                 }
             },
             "Report timing manager",
             py::arg("ign_cutoff") = false,
             py::arg("serialize") = false,
             py::arg("serial_filename") = "");
    //------------------------------------------------------------------------//
    man.def("__str__",
             [=] (py::object man)
             {
                 manager_t* _man
                         = man.cast<manager_wrapper*>()->get();
                 std::stringstream ss;
                 bool ign_cutoff = true;
                 bool endline = false;
                 _man->report(ss, ign_cutoff, endline);
                 return ss.str();
             },
             "Stringify the timing manager report");
    //------------------------------------------------------------------------//
    man.def("set_output_file",
             [=] (py::object man, std::string fname)
             {
                 manager_t* _man = man.cast<manager_wrapper*>()->get();
                 auto locals = py::dict("fname"_a = fname);
                 py::exec(R"(
                          import timemory as tim
                          tim.options.set_report(fname)
                          )", py::globals(), locals);
                 _man->set_output_stream(fname);
             },
             "Set the output stream file");
    //------------------------------------------------------------------------//
    man.def("size",
             [=] (py::object man)
             { return man.cast<manager_wrapper*>()->get()->size(); },
             "Size of timing manager");
    //------------------------------------------------------------------------//
    man.def("clear",
             [=] (py::object man)
             { man.cast<manager_wrapper*>()->get()->clear(); },
             "Clear the timing manager");
    //------------------------------------------------------------------------//
    man.def("write_overhead",
            [=] (py::object man, std::string fname)
            {
                auto locals = py::dict("fname"_a = fname);
                py::exec(R"(
                         import timemory.options as options
                         options.ensure_directory_exists(fname)
                         )",
                         py::globals(), locals);
                man.cast<manager_wrapper*>()->get()->write_overhead(fname);
            },
            "Write TiMemory overhead to file");
    //------------------------------------------------------------------------//
    man.def("serialize",
             [=] (py::object man, std::string fname = "")
             {
                  if(fname.empty())
                  {
                      auto locals = py::dict();
                      py::exec(R"(
                               import timemory.options as options
                               import os

                               result = options.serial_filename
                               if not options.output_dir in result:
                                   result = os.path.join(options.output_dir, result)
                               options.ensure_directory_exists(result)
                               )", py::globals(), locals);
                      fname = locals["result"].cast<std::string>();
                  }
                  man.cast<manager_wrapper*>()->get()->write_serialization(fname);
                  return fname;
             },
             "Serialize the timing manager to JSON",
             py::arg("fname") = "");
    //------------------------------------------------------------------------//
    man.def("set_max_depth",
             [=] (py::object man, int depth)
             { man.cast<manager_wrapper*>()->get()->set_max_depth(depth); },
             "Set the max depth of the timers");
    //------------------------------------------------------------------------//
    man.def("get_max_depth",
             [=] (py::object man)
             { return man.cast<manager_wrapper*>()->get()->get_max_depth(); },
             "Get the max depth of the timers");
    //------------------------------------------------------------------------//
    man.def("at",
             [=] (py::object man, int i)
             {
                 tim_timer_t& _t = man.cast<manager_wrapper*>()->get()->at(i);
                 return &_t;
             },
             "Set the max depth of the timers",
             py::return_value_policy::reference);
    //------------------------------------------------------------------------//
    man.def("merge",
             [=] (py::object man, bool div_clocks)
             { man.cast<manager_wrapper*>()->get()->merge(div_clocks); },
             "Merge the thread-local timers",
             py::arg("div_clocks") = true);
    //------------------------------------------------------------------------//
    man.def("json",
             [=] (py::object man)
             {
                 std::stringstream ss;
                 man.cast<manager_wrapper*>()->get()->write_json(ss);
                 py::module _json = py::module::import("json");
                 return _json.attr("loads")(ss.str());
             }, "Get JSON serialization of timing manager");
    //------------------------------------------------------------------------//
    man.def("__iadd__",
             [=] (py::object man, py::object _rss)
             {
                 *(man.cast<manager_wrapper*>()->get()) +=
                         *(_rss.cast<rss_usage_t*>());
                 return man;
             },
             "Add RSS measurement");
    //------------------------------------------------------------------------//
    man.def("__isub__",
             [=] (py::object man, py::object _rss)
             {
                 *(man.cast<manager_wrapper*>()->get()) -=
                         *(_rss.cast<rss_usage_t*>());
                 return man;
             },
             "Subtract RSS measurement");
    //------------------------------------------------------------------------//
    man.def("write_ctest_notes",
             [=] (py::object man, std::string directory, bool append)
             {
                 py::list filenames = man.attr("reported_files").cast<py::list>();

                 std::stringstream ss;
                 ss << std::endl;
                 ss << "IF(NOT DEFINED CTEST_NOTES_FILES)" << std::endl;
                 ss << "    SET(CTEST_NOTES_FILES )" << std::endl;
                 ss << "ENDIF(NOT DEFINED CTEST_NOTES_FILES)" << std::endl;
                 ss << std::endl;

                 // loop over ASCII report filenames
                 for(const auto& itr : filenames)
                 {
                     std::string fname = itr.cast<std::string>();
                 #if defined(_WIN32)
                     while(fname.find("\\") != std::string::npos)
                         fname = fname.replace(fname.find("\\"), 1, "/");
                 #endif
                     ss << "LIST(APPEND CTEST_NOTES_FILES \"" << fname << "\")" << std::endl;
                 }

                 ss << std::endl;
                 ss << "IF(NOT \"${CTEST_NOTES_FILES}\" STREQUAL \"\")" << std::endl;
                 ss << "    LIST(REMOVE_DUPLICATES CTEST_NOTES_FILES)" << std::endl;
                 ss << "ENDIF(NOT \"${CTEST_NOTES_FILES}\" STREQUAL \"\")" << std::endl;
                 ss << std::endl;

                 // create directory (easier in Python)
                 auto locals = py::dict("directory"_a = directory);
                 py::exec(R"(
                          import os

                          if not os.path.exists(directory) and directory != '':
                              os.makedirs(directory)

                          file_path = os.path.join(directory, "CTestNotes.cmake")
                          )",
                          py::globals(), locals);

                 std::string file_path = locals["file_path"].cast<std::string>();
                 std::ofstream outf;
                 if(append)
                     outf.open(file_path.c_str(), std::ios::app);
                 else
                     outf.open(file_path.c_str());

                 if(outf)
                     outf << ss.str();
                 outf.close();

                 return file_path;
             },
             "Write a CTestNotes.cmake file",
             py::arg("directory") = ".",
             py::arg("append") = false);
    //------------------------------------------------------------------------//


    //========================================================================//
    //
    //                      AUTO TIMER
    //
    //========================================================================//
    auto_timer.def(py::init(auto_timer_init),
                   "Initialization",
                   py::arg("key") = "",
                   py::arg("report_at_exit") = false,
                   py::arg("nback") = 1,
                   py::arg("added_args") = false,
                   py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    auto_timer.def("local_timer",
                   [=] (py::object _auto_timer)
                   { return _auto_timer.cast<auto_timer_t*>()->local_timer(); },
                   "Get the timer for the auto-timer instance");
    //------------------------------------------------------------------------//
    auto_timer.def("global_timer",
                   [=] (py::object _auto_timer)
                   { return _auto_timer.cast<auto_timer_t*>()->local_timer().summation_timer(); },
                   "Get the timer for all the auto-timer instances (from manager)");
    //------------------------------------------------------------------------//
    auto_timer.def("__str__",
                   [=] (py::object _pyauto_timer)
                   {
                       std::stringstream _ss;
                       auto_timer_t* _auto_timer
                               = _pyauto_timer.cast<auto_timer_t*>();
                       tim_timer_t _local = _auto_timer->local_timer();
                       _local.stop();
                       tim_timer_t _global = *_auto_timer->local_timer().summation_timer();
                       _global += _local;
                       _global.format()->align_width(false);
                       _global.report(_ss, false, true);
                       return _ss.str();
                   },
                   "Print the auto timer");
    //------------------------------------------------------------------------//
    timer_decorator.def(py::init(timer_decorator_init),
                        "Initialization",
                        py::return_value_policy::automatic);
    //------------------------------------------------------------------------//


    //========================================================================//
    //
    //                      RSS USAGE
    //
    //========================================================================//
    rss_usage.def(py::init(rss_usage_init),
                  "Initialization of RSS measurement class",
                  py::return_value_policy::take_ownership,
                  py::arg("prefix") = "",
                  py::arg("record") = false,
                  py::arg("format") = "");
    //------------------------------------------------------------------------//
    rss_usage.def("record",
                  [=] (py::object self)
                  {
                      self.cast<rss_usage_t*>()->record();
                  },
                  "Record the RSS usage");
    //------------------------------------------------------------------------//
    rss_usage.def("__str__",
                  [=] (py::object self)
                  {
                      std::stringstream ss;
                      ss << *(self.cast<rss_usage_t*>());
                      return ss.str();
                  },
                  "Stringify the rss usage");
    //------------------------------------------------------------------------//
    rss_usage.def("__iadd__",
                  [=] (py::object self, py::object rhs)
                  {
                      *(self.cast<rss_usage_t*>())
                            += *(rhs.cast<rss_usage_t*>());
                      return self;
                  },
                  "Add rss usage");
    //------------------------------------------------------------------------//
    rss_usage.def("__isub__",
                  [=] (py::object self, py::object rhs)
                  {
                      *(self.cast<rss_usage_t*>())
                            -= *(rhs.cast<rss_usage_t*>());
                      return self;
                  },
                  "Subtract rss usage");
    //------------------------------------------------------------------------//
    rss_usage.def("__add__",
                  [=] (py::object self, py::object rhs)
                  {
                      rss_usage_t* _rss
                            = new rss_usage_t(*(self.cast<rss_usage_t*>()));
                      *_rss += *(rhs.cast<rss_usage_t*>());
                      return _rss;
                  },
                  "Add rss usage",
                  py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    rss_usage.def("__sub__",
                  [=] (py::object self, py::object rhs)
                  {
                      rss_usage_t* _rss
                            = new rss_usage_t(*(self.cast<rss_usage_t*>()));
                      *_rss -= *(rhs.cast<rss_usage_t*>());
                      return _rss;
                  },
                  "Subtract rss usage",
                  py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    rss_usage.def("current",
                  [=] (py::object self)
                  {
                      return self.cast<rss_usage_t*>()->current();
                  },
                  "Return the current rss usage");
    //------------------------------------------------------------------------//
    rss_usage.def("peak",
                  [=] (py::object self)
                  {
                      return self.cast<rss_usage_t*>()->peak();
                  },
                  "Return the current rss usage");
    //------------------------------------------------------------------------//
    rss_usage.def("get_format",
              [=] (py::object self)
              {
                  rss_usage_t* _self = self.cast<rss_usage_t*>();
                  auto _fmt = _self->format();
                  if(!_fmt.get())
                  {
                      _self->set_format(rss_format_t());
                      _fmt = _self->format();
                  }
                  return _fmt.get();
              },
              "Set the format of the RSS usage",
              py::return_value_policy::reference_internal);
    //------------------------------------------------------------------------//
    rss_usage.def("set_format",
                  [=] (py::object rss, py::object fmt)
                  {
                      rss_usage_t* _rss = rss.cast<rss_usage_t*>();
                      rss_format_t* _fmt = fmt.cast<rss_format_t*>();
                      _rss->set_format(*_fmt);
                  },
                  "Set the format of the RSS usage");
    //------------------------------------------------------------------------//


    //========================================================================//
    //
    //                      RSS USAGE DELTA
    //
    //========================================================================//
    rss_delta.def(py::init(rss_delta_init),
                  "Initialization of RSS measurement class",
                  py::return_value_policy::take_ownership,
                  py::arg("prefix") = "",
                  py::arg("format") = "");
    //------------------------------------------------------------------------//
    rss_delta.def("init",
                  [=] (py::object self)
                  {
                      self.cast<rss_delta_t*>()->init();
                  },
                  "Initialize the RSS delta usage");
    //------------------------------------------------------------------------//
    rss_delta.def("record",
                  [=] (py::object self)
                  {
                      self.cast<rss_delta_t*>()->record();
                  },
                  "Record the RSS delta usage");
    //------------------------------------------------------------------------//
    rss_delta.def("__str__",
                  [=] (py::object self)
                  {
                      std::stringstream ss;
                      ss << *(self.cast<rss_delta_t*>());
                      return ss.str();
                  },
                  "Stringify the RSS delta usage");
    //------------------------------------------------------------------------//
    rss_delta.def("__iadd__",
                  [=] (py::object self, py::object rhs)
                  {
                      *(self.cast<rss_delta_t*>())
                            += *(rhs.cast<rss_usage_t*>());
                      return self;
                  },
                  "Add rss delta usage");
    //------------------------------------------------------------------------//
    rss_delta.def("__isub__",
                  [=] (py::object self, py::object rhs)
                  {
                      *(self.cast<rss_delta_t*>())
                            -= *(rhs.cast<rss_usage_t*>());
                      return self;
                  },
                  "Subtract rss delta usage");
    //------------------------------------------------------------------------//
    rss_delta.def("__add__",
                  [=] (py::object self, py::object rhs)
                  {
                      rss_delta_t* _rss
                            = new rss_delta_t(*(self.cast<rss_delta_t*>()));
                      *_rss += *(rhs.cast<rss_usage_t*>());
                      return _rss;
                  },
                  "Add rss delta usage",
                  py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    rss_delta.def("__sub__",
                  [=] (py::object self, py::object rhs)
                  {
                      rss_delta_t* _rss
                            = new rss_delta_t(*(self.cast<rss_delta_t*>()));
                      *_rss -= *(rhs.cast<rss_usage_t*>());
                      return _rss;
                  },
                  "Subtract delta rss usage",
                  py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    rss_delta.def("total",
                  [=] (py::object self)
                  {
                      return new rss_usage_t(self.cast<rss_delta_t*>()->total());
                  },
                  "Return the total rss usage",
                  py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    rss_delta.def("self",
                  [=] (py::object self)
                  {
                      return new rss_usage_t(self.cast<rss_delta_t*>()->self());
                  },
                  "Return the self rss usage",
                  py::return_value_policy::take_ownership);
    //------------------------------------------------------------------------//
    rss_delta.def("get_format",
              [=] (py::object self)
              {
                  rss_delta_t* _self = self.cast<rss_delta_t*>();
                  auto _fmt = _self->format();
                  if(!_fmt.get())
                  {
                      _self->set_format(rss_format_t());
                      _fmt = _self->format();
                  }
                  return _fmt.get();
              },
              "Set the format of the RSS usage",
              py::return_value_policy::reference_internal);
    //------------------------------------------------------------------------//
    rss_delta.def("set_format",
                  [=] (py::object rss, py::object fmt)
                  {
                      rss_delta_t* _rss = rss.cast<rss_delta_t*>();
                      rss_format_t* _fmt = fmt.cast<rss_format_t*>();
                      _rss->set_format(*_fmt);
                  },
                  "Set the format of the RSS usage");
    //------------------------------------------------------------------------//

    //========================================================================//
    //
    //                      MAIN timemory MODULE (part 2)
    //
    //========================================================================//
    // keep manager from being garbage collected
    tim.attr("_static_manager") = new manager_wrapper();
    tim.attr("timing_manager") = man;
    //------------------------------------------------------------------------//
    tim.def("report",
            [=] (bool ign_cutoff = true, bool endline = true)
            { manager_t::instance()->report(ign_cutoff, endline); },
            "Report the timing manager (default: ign_cutoff = True, endline = True)",
            py::arg("ign_cutoff") = true, py::arg("endline") = true);
    //------------------------------------------------------------------------//
    tim.def("clear",
            [=] ()
            { manager_t::instance()->clear(); },
            "Clear the timing manager");
    //------------------------------------------------------------------------//
    tim.def("size",
            [=] ()
            { return manager_t::instance()->size(); },
            "Size of the timing manager");
    //------------------------------------------------------------------------//
    tim.def("set_exit_action",
            [=] (py::function func)
            {
                auto _func = [=] (int errcode) -> void
                {
                    func(errcode);
                };
                //typedef tim::signal_settings::signal_function_t signal_function_t;
                typedef std::function<void(int)> signal_function_t;
                using std::placeholders::_1;
                signal_function_t _f = std::bind<void>(_func, _1);
                tim::signal_settings::set_exit_action(_f);
            },
            "Set the exit action when a signal is raised -- function must accept integer");
    //------------------------------------------------------------------------//


    //========================================================================//
    //
    //      Signals submodule
    //
    //========================================================================//
    py::module sig = tim.def_submodule("signals",       "Signals submodule");
    //------------------------------------------------------------------------//
    py::enum_<sys_signal_t> sys_signal_enum(sig, "sys_signal", py::arithmetic(),
                                            "Signals for TiMemory module");
    //------------------------------------------------------------------------//
    sys_signal_enum
            .value("Hangup", sys_signal_t::sHangup)
            .value("Interrupt", sys_signal_t::sInterrupt)
            .value("Quit", sys_signal_t::sQuit)
            .value("Illegal", sys_signal_t::sIllegal)
            .value("Trap", sys_signal_t::sTrap)
            .value("Abort", sys_signal_t::sAbort)
            .value("Emulate", sys_signal_t::sEmulate)
            .value("FPE", sys_signal_t::sFPE)
            .value("Kill", sys_signal_t::sKill)
            .value("Bus", sys_signal_t::sBus)
            .value("SegFault", sys_signal_t::sSegFault)
            .value("System", sys_signal_t::sSystem)
            .value("Pipe", sys_signal_t::sPipe)
            .value("Alarm", sys_signal_t::sAlarm)
            .value("Terminate", sys_signal_t::sTerminate)
            .value("Urgent", sys_signal_t::sUrgent)
            .value("Stop", sys_signal_t::sStop)
            .value("CPUtime", sys_signal_t::sCPUtime)
            .value("FileSize", sys_signal_t::sFileSize)
            .value("VirtualAlarm", sys_signal_t::sVirtualAlarm)
            .value("ProfileAlarm", sys_signal_t::sProfileAlarm);
    // ---------------------------------------------------------------------- //


    //========================================================================//
    //
    //      Options submodule
    //
    //========================================================================//
    py::module opts = tim.def_submodule("options", "I/O options submodule");
    // ---------------------------------------------------------------------- //
    opts.attr("report_file") = false;
    opts.attr("serial_file") = true;
    opts.attr("use_timers") = true;
    opts.attr("max_timer_depth") = std::numeric_limits<uint16_t>::max();
    opts.attr("report_filename") = "timing_report.out";
    opts.attr("serial_filename") = "timing_report.json";
    opts.attr("output_dir") = ".";
    opts.attr("echo_dart") = false;
    opts.attr("ctest_notes") = false;
    opts.attr("matplotlib_backend") = std::string("default");

    // ---------------------------------------------------------------------- //
    opts.def("default_max_depth",
            [=]() { return std::numeric_limits<uint16_t>::max(); },
            "Return the default max depth");
    // ---------------------------------------------------------------------- //
    opts.def("safe_mkdir",
             [=] (std::string directory)
             {
                 auto locals = py::dict("directory"_a = directory);
                 py::exec(R"(
                          import os
                          if not os.path.exists(directory) and directory != '':
                              os.makedirs(directory)
                          )",
                          py::globals(), locals);

             },
             "if [ ! -d <directory> ]; then mkdir -p <directory> ; fi");
    // ---------------------------------------------------------------------- //
    opts.def("ensure_directory_exists",
             [=] (std::string file_path)
             {
                 auto locals = py::dict("file_path"_a = file_path);
                 py::exec(R"(
                          import os

                          directory = os.path.dirname(file_path)
                          if not os.path.exists(directory) and directory != '':
                              os.makedirs(directory)
                          )",
                          py::globals(), locals);

             },
             "mkdir -p $(basename file_path)");
    // ---------------------------------------------------------------------- //
    opts.def("set_report",
             [=] (std::string fname)
             {
                 std::stringstream ss;
                 std::string output_dir = opts.attr("output_dir").cast<std::string>();
                 if(fname.find(output_dir) != 0)
                     ss << output_dir;
                 if(ss.str().length() > 0 && ss.str()[ss.str().length()-1] != '/')
                     ss << "/";
                 ss << fname;
                 opts.attr("report_filename") = ss.str().c_str();
                 opts.attr("report_file") = true;
                 return ss.str();
             },
             "Set the ASCII report filename");

    // ---------------------------------------------------------------------- //
    opts.def("set_serial",
             [=] (std::string fname)
             {
                 std::stringstream ss;
                 std::string output_dir = opts.attr("output_dir").cast<std::string>();
                 if(fname.find(output_dir) != 0)
                     ss << output_dir;
                 if(ss.str().length() > 0 && ss.str()[ss.str().length()-1] != '/')
                     ss << "/";
                 ss << fname;
                 opts.attr("serial_filename") = ss.str().c_str();
                 opts.attr("serial_file") = true;
                 return ss.str();
             },
             "Set the JSON serialization filename");
    // ---------------------------------------------------------------------- //
    opts.def("add_arguments",
             [=] (py::object parser = py::none(), std::string fname = "")
             {
                 auto locals = py::dict("parser"_a = parser,
                                        "fname"_a = fname);
                 py::exec(R"(
                          import sys
                          import os
                          from os.path import join
                          import argparse
                          import timemory

                          if parser is None:
                             parser = argparse.ArgumentParser()

                          # Function to add default output arguments
                          def get_file_tag(fname):
                              import os
                              _l = os.path.basename(fname).split('.')
                              if len(_l) > 1:
                                  _l.pop()
                              return ("{}".format('_'.join(_l)))

                          def_fname = "timing_report"
                          if fname != "":
                              def_fname = '_'.join(["timing_report", get_file_tag(fname)])

                          parser.add_argument('--output-dir', required=False,
                                              default='.', type=str, help="Output directory")
                          parser.add_argument('--filename', required=False,
                                              default=def_fname, type=str,
                                              help="Filename for timing report w/o directory and w/o suffix")
                          parser.add_argument('--disable-timers', required=False,
                                              action='store_false',
                                              dest='use_timers',
                                              help="Disable timers for script")
                          parser.add_argument('--enable-timers', required=False,
                                              action='store_true',
                                              dest='use_timers', help="Enable timers for script")
                          parser.add_argument('--disable-timer-serialization',
                                              required=False, action='store_false',
                                              dest='serial_file',
                                              help="Disable serialization for timers")
                          parser.add_argument('--enable-timer-serialization',
                                              required=False, action='store_true',
                                              dest='serial_file',
                                              help="Enable serialization for timers")
                          parser.add_argument('--max-timer-depth',
                                              help="Maximum timer depth",
                                              type=int,
                                              default=timemory.options.default_max_depth())
                          parser.add_argument('--enable-dart',
                                              help="Print DartMeasurementFile tag for plots",
                                              required=False, action='store_true')
                          parser.add_argument('--write-ctest-notes',
                                              help="Write a CTestNotes.cmake file for TiMemory ASCII output",
                                              required=False, action='store_true')

                          parser.set_defaults(use_timers=True)
                          parser.set_defaults(serial_file=True)
                          parser.set_defaults(enable_dart=False)
                          parser.set_defaults(write_ctest_notes=False)
                          )",
                          py::globals(), locals);
                 return locals["parser"].cast<py::object>();
             },
             "Function to add default output arguments",
             py::arg("parser") = py::none(), py::arg("fname") = "");
    // ---------------------------------------------------------------------- //
    opts.def("parse_args",
             [=] (py::object args)
             {
                 auto locals = py::dict("args"_a = args);
                 py::exec(R"(
                          import sys
                          import os
                          import timemory

                          # Function to add default output arguments
                          timemory.options.serial_file = args.serial_file
                          timemory.options.use_timers = args.use_timers
                          timemory.options.max_timer_depth = args.max_timer_depth
                          timemory.options.output_dir = args.output_dir
                          timemory.options.echo_dart = args.enable_dart
                          timemory.options.ctest_notes = args.write_ctest_notes

                          if args.filename:
                              timemory.options.set_report("{}.{}".format(args.filename, "out"))
                              timemory.options.set_serial("{}.{}".format(args.filename, "json"))

                          timemory.toggle(timemory.options.use_timers)
                          timemory.set_max_depth(timemory.options.max_timer_depth)
                          )",
                          py::globals(), locals);
             },
             "Function to handle the output arguments");
    // ---------------------------------------------------------------------- //
    opts.def("add_arguments_and_parse",
             [=] (py::object parser = py::none(), std::string fname = "")
             {
                 auto locals = py::dict("parser"_a = parser,
                                        "fname"_a = fname);
                 py::exec(R"(
                          import timemory

                          # Combination of timing.add_arguments and timing.parse_args but returns
                          parser = timemory.options.add_arguments(parser, fname)
                          args = parser.parse_args()
                          timemory.options.parse_args(args)
                          )",
                          py::globals(), locals);
                 return locals["args"].cast<py::object>();
             },
             "Combination of timing.add_arguments and timing.parse_args but returns",
             py::arg("parser") = py::none(), py::arg("fname") = "");
    // ---------------------------------------------------------------------- //
    opts.def("add_args_and_parse_known",
             [=] (py::object parser = py::none(), std::string fname = "")
             {
                 auto locals = py::dict("parser"_a = parser,
                                        "fname"_a = fname);
                 py::exec(R"(
                          import timemory

                          # Combination of timing.add_arguments and timing.parse_args but returns
                          parser = timemory.options.add_arguments(parser, fname)
                          args, left = parser.parse_known_args()
                          timemory.options.parse_args(args)
                          # replace sys.argv with unknown args only
                          sys.argv = sys.argv[:1]+left
                          )",
                          py::globals(), locals);
                 return locals["args"].cast<py::object>();
             },
             "Combination of timing.add_arguments and timing.parse_args. Returns "
             "TiMemory args and replaces sys.argv with the unknown args (used to "
             "fix issue with unittest module)",
             py::arg("parser") = py::none(), py::arg("fname") = "");
    // ---------------------------------------------------------------------- //

}
