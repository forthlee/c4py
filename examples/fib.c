#include <stdio.h>

int fib(int i) {
    if (i<2) {
        return i;
    }
    return fib(i - 1) + fib(i - 2);
}

int main()
{
    printf("fib(10)=%d\n", fib(10));
    return 0;
}
