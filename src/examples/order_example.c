#include <stdatomic.h>
#include <stdbool.h>
#include <stdio.h>
#include <threads.h>
#include <unistd.h>
int v = 0;
bool v_ready = false;

int threadA(void *args)
{
    v = 42;
    v_ready = true;

    return 0;
}

int threadB(void *args)
{
    for (int i = 0; i < 3; i++) {
        if (!v_ready) {
            printf("false: %d\n", v);
        }
        if (v_ready) {
            printf("true: %d\n", v);
        }
    }
    return 0;
}

int main()
{
    thrd_t A, B;
    thrd_create(&B, threadB, NULL);
    thrd_create(&A, threadA, NULL);
    sleep(1);
    return 0;
}
