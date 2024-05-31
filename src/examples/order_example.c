#include <stdatomic.h>
#include <stdbool.h>
int v = 0;
atomic_bool v_ready = false;

void *threadA()
{
    v = 42;
    v_ready = true;
}
int bv;

void *threadB()
{
    while(!v_ready) { /* wait */ }
    bv = v;
    /* Do something */
}
