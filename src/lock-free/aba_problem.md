# ABA problem

CAS has been introduced as one of the read-modify-write operations.
However, the target object not changing does not necessarily mean that no other threads modified it halfway through.
If the target object is changed by another thread and then changed back, the result of comparison would still be equal.
In this case, the target object has indeed been modified, yet the operation appears unchanged, compromising its atomicity.
We call this *ABA problem*.
Consider the following scenario,

```c
{{#include ../../examples/simple_aba_example.c}}
```

The execution result would be:

```c
    A: v = 42
    B: v = 47
    B: v = 42
    A: v = 52
```

In the example provided, the ABA problem causes thread A to be unaware that variable `v` has been altered.
Since the comparison result indicates that `v` is unchanged, `v + 10` is swapped in.
The two flags pin the interleaving down rather than leaving it to the scheduler:
`a_has_read` holds thread B back until A has loaded `v`,
since B finishing first would leave nothing for A to be misled about,
and `b_done` holds A back until B has changed `v` and changed it back.
In a real-world scenario, instead of this handshake, thread A could be paused by a context switch to another task, including preemption by a higher-priority task.
This example seems harmless, but things can get nasty when atomic <small>RMW</small> operations are used in more complex data structures.

In a broader context, the ABA problem occurs when changes occur between loading and comparing, but the comparing mechanism is unable to identify that the state of the target object is not the latest, yielding a false positive result.

Returning to the thread pool example in [Read-modify-write](../read-modify-write.html), it contains the ABA problem as well.
In the `worker` function, we have a thread trying to claim the job.

```c
    job_t *job = atomic_load(&thrd_pool->head->prev);
    ...
    while (job != &thrd_pool->head->job &&
           !atomic_compare_exchange_weak(&thrd_pool->head->prev, &job,
                                         job->prev))
        ;
```

Consider the following scenario:

1.  There is only one job left.

2.  Thread A loads the pointer to the job by `atomic_load()`.

3.  Thread A is preempted.

4.  Thread B claims the job and successfully updates `thrd_pool->head->prev`.

5.  Thread B sets the thread pool state to idle.

6.  The main thread finishes waiting and adds more jobs.

7.  The memory allocator reuses the recently freed memory for new jobs.

8.  Fortunately, the first added job has the same address as the one thread A held.

9.  Thread A is back in running state. The comparison result is equal so it updates `thrd_pool->head->prev` with the old `job->prev`, which is already a dangling pointer.

10. Another thread loads the dangling pointer from `thrd_pool->head->prev`.

Notice that even though `job->prev` is not loaded explicitly before the comparison, the compiler could place loading instructions before the comparison.
In the end, the dangling pointer could either point to garbage or trigger a segmentation fault.
It could be even worse if a nested ABA problem occurs in thread B.
Also, using a memory pool could make allocating a job at the same address more likely, creating more opportunities for the ABA problem to occur.
In fact, pre-allocated memory should be used to achieve lock-free behavior since `malloc` could involve a mutex in a multi-threaded environment.

Being unable to determine whether the target object has been changed through comparison could result in a false positive when the return value of CAS is true.
Thus, the atomicity provided by CAS is not guaranteed.
The general concept of solving this problem involves adding more information to make different states distinguishable, and then deciding whether to act on the old state or retry with the new state.
If acting on the old state is chosen, then safe memory reclamation should be considered as memory may have already been freed by other threads.
More aggressively, one might consider a programming paradigm where each operation on the target object has no side effects that modify it.
In a later section, we will introduce a different way of implementing atomic <small>RMW</small> operations using LL/SC instructions. The exclusive status provided by LL/SC instructions avoids the pitfall introduced by comparison.

To make different states distinguishable, a common solution is to increment a version number each time the target object is changed.
Bundling the target object and version into a comparison ensures that each change marks a distinguishable result.
Given a sufficiently large version number, there should be no repeated version numbers.
There are multiple methods for storing the version number, depending on the evaluation of the duration before a version number wraps around.
In the thread pool example, the target object is a pointer. The unused bits in a pointer can be utilized to store the version number.
In addition to embedding the version number into a pointer, we could consider utilizing an additional 32-bit or 64-bit value next to the target object for the version number.
This requires the compare-and-swap instruction to be capable of comparing a wider size at once.
Sometimes, this is referred to as *double-width compare-and-swap*.
On x86-64 processors, atomic instructions that load or store more than one CPU word require additional hardware support.
You can use `grep cx16 /proc/cpuinfo` to check if the processor supports 16-byte compare-and-swap.
For hardware that does not support the desired size, software implementations that may involve locks are used instead, as mentioned in [Arbitrarily-sized "atomic" types](../Arbitrarily-sized_atomic_types.html).
Returning to the example, the ABA problem in the following code is fixed by using a version number that increments each time a job is added to the empty queue. On x86-64, add the compiler flag `-mcx16` to enable 16-byte compare-and-swap in the `worker` function.[^1]

```c
{{#include ../../examples/rmw_example_aba.c}}
```

Notice that, in the `struct idle_job`, a union is used for type punning, which bundles the pointer and version number for compare-and-swap.
Directly casting a job pointer to a pointer that points to a 16-byte object is undefined behavior (due to having different alignment); type punning is used instead.
By using this technique, `struct idle_job` can still be accessed normally in other places, minimizing code modification.
Compiler optimizations are conservative on type punning, but it is acceptable for atomic operations.
See [Atomic fusion](../atomic_fusion.html).
Another way to prevent the ABA problem in the example is to use safe memory reclamation mechanisms.
Unlike the previously mentioned approach of acting on the old state, the address of a job is not freed until no thread is using it.
This prevents the memory allocator or memory pool from reusing the address and causing problems.

[^1]: When using `-mcx16`, programs relying on 16-byte atomic operations (e.g., using `__int128`) may require linking with `-latomic`, as these operations are implemented via function calls to `libatomic` on some systems. See <https://gcc.gnu.org/bugzilla/show_bug.cgi?id=104688>.
