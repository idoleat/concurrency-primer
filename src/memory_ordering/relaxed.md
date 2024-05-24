# Relaxed

Relaxed atomic operations are useful for variables shared between threads where *no specific order* of operations is needed.
Although it may seem like a niche requirement, such scenarios are quite common.

Refer back to our discussions on \secref{atomicity} and \secref{rmw} operations, <!--FIXME-->
where a worker thread increments a counter that a <small>UI</small> thread then reads.
In this case, the counter can be incremented using `fetch_add(1, memory_order_relaxed)` because the only requirement is atomicity;
the counter itself does not coordinate synchronization.

Relaxed operations are also beneficial for managing flags shared between threads.
For example, a thread might continuously run until it receives a signal to exit:
```cpp
atomic_bool stop(false);

void worker()
{
    while (!stop.load(memory_order_relaxed)) {
        // Do good work.
    }
}

int main()
{
    launchWorker();
    // Wait some...
    stop = true; // seq_cst
    joinWorker();
}
```
We do not care if the contents of the loop are rearranged around the load.
Nothing bad will happen so long as `stop` is only used to tell the worker to exit, and not to "announce" any new data.

Finally, relaxed loads are commonly used with <small>CAS</small> loops.
Return to our lock-free multiply:
```cpp
void atomicMultiply(int by)
{
    int expected = foo.load(memory_order_relaxed);

    while (!foo.compare_exchange_weak(
        expected, expected * by,
        memory_order_release,
        memory_order_relaxed)) {
        /* empty loop */
    }
}
```
All of the loads can be relaxed as we do not need to enforce any order until we have successfully modified our value.
The initial load of `expected` is not strictly necessary but can help avoid an extra loop iteration if `foo` remains unmodified by other threads before the <small>CAS</small> operation.
