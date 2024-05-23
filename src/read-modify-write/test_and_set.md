# Test and set

*Test-and-set* works on a Boolean value:
we read it, set it to `true`, and provide the value it held beforehand.
C and C++ offer a type dedicated to this purpose, called `atomic_flag`.
We could use it to build a simple spinlock:

```c
atomic_flag af = ATOMIC_FLAG_INIT;

void lock()
{
    while (atomic_flag_test_and_set(&af)) { /* wait */ }
}

void unlock() { atomic_flag_clear(&af); }
```

If we call `lock()` and the previous value is `false`,
we are the first to acquire the lock,
and can proceed with exclusive access to whatever the lock protects.
If the previous value is `true`,
someone else has acquired the lock and we must wait until they release it by clearing the flag.
