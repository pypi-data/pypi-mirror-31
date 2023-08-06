
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <timemory/ctimemory.h>

int64_t fibonacci(int64_t n)
{
    void* timer = NULL;
    if (n > 36)
    {
        int length = snprintf( NULL, 0, "%lli", (long long int) n );
        char* str = malloc( length + 1 );
        snprintf( str, length + 3, "[%lli]", (long long int) n );
        timer = TIMEMORY_AUTO_TIMER(str);
        free(str);
    }
    int64_t _n = (n < 2) ? 1L : (fibonacci(n-2) + fibonacci(n-1));
    FREE_TIMEMORY_AUTO_TIMER(timer);
    return _n;
}

int main(int argc, char** argv)
{
    // modify recording memory
    if(argc > 1)
        TIMEMORY_RECORD_MEMORY(atoi(argv[1]));

    printf("%s @ %i\n", __FUNCTION__, __LINE__);

    void* timer = TIMEMORY_AUTO_TIMER("");
    int64_t n = fibonacci(44);
    printf("\nANSWER = %lli\n", (long long int) n);
    FREE_TIMEMORY_AUTO_TIMER(timer);

    TIMEMORY_PRINT();
    TIMEMORY_REPORT("test_output/c_timing_report");

    return 0;
}
