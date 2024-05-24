# Spurious LL/SC failures

It is impractical for <small>CPU</small> hardware to track load-linked addresses for each byte within a system due to the immense resource requirements.
To mitigate this, many processors monitor these operations at a broader scale, like the cache line level.
Consequently, a <small>SC</small> operation may fail if any part of the monitored block is written to,
not just the specific address that was load-linked.

This limitation poses a particular challenge for operations like compare and swap,
highlighting the essential purpose of `compare_exchange_weak`.
Consider, for example, the task of atomically multiplying a value without an architecture-specific atomic read-multiply-write instruction.
```cpp
void atomicMultiply(int by)
{
    int expected = foo;
    // Which CAS should we use?
    while (!foo.compare_exchange_?(expected, expected * by)) {
        // Empty loop.
        // (On failure, expected is updated with foo's most recent value.)
    }
}
```
Many lockless algorithms use <small>CAS</small> loops like this to atomically update a variable when calculating its new value is not atomic.
They:
1. Read the variable.
2. Perform some (non-atomic) operation on its value.
3. <small>CAS</small> the new value with the previous one.
4. If the <small>CAS</small> failed, another thread beat us to the punch, so try again.

If we use `compare_exchange_strong` for this family of algorithms,
the compiler must emit nested loops:
an inner one to protect us from spurious <small>SC</small> failures,
and an outer one which repeatedly performs our operation until no other thread has interrupted us.
But unlike the `_strong` version,
a weak <small>CAS</small> is allowed to fail spuriously, just like the <small>LL/SC</small> mechanism that implements it.
So, with `compare_exchange_weak`,
the compiler is free to generate a single loop,
since we do not care about the difference between retries from spurious <small>SC</small> failures and retries caused by another thread modifying our variable.
