# Example

The following example code is a simplified implementation of a thread pool, which demonstrates the use of the C11 atomic library.

```c
{{#include ../../examples/rmw_example.c}}
```

Stdout of the program is:

```c
PI calculated with 100 terms: 3.141592653589793
```

**Exchange**
In function `tpool_destroy`, `atomic_exchange(&thrd_pool->state, cancelled)` reads the current state and replaces it with "cancelled".
A warning message is printed if the pool is destroyed while workers are still "running".
If the exchange is not performed atomically, we may initially get the state as "running". Subsequently, a thread could set the state to "cancelled" after finishing the last one, resulting in a false warning.

**Test and set**
In this example, the scenario is as follows:
First, the main thread initially acquires a lock `future->flag` and then sets it true,
which is akin to creating a job and then transferring its ownership to the worker.
Subsequently, the main thread will be blocked until the worker clears the flag.
This indicates that the main thread will wait until the worker completes the job and returns ownership to the main thread, allowing the two threads to cooperate correctly.

**Fetch and...**
In the function `tpool_destroy`, `atomic_fetch_and` is utilized as a means to set the state to "idle".
Yet, in this case, it is not necessary, as the pool needs to be reinitialized for further use regardless.
Its return value could be further utilized, for instance, to report the previous state and perform additional actions.

**Compare and swap**
Once threads are created in the thread pool as workers, they will continuously search for jobs to do.
Jobs are taken from the tail of the job queue.
To take a job without being taken by another worker halfway through, we need to atomically change the pointer to the last job.
Otherwise, the last job is under race.
The while loop in the function `worker`,

```c
while (job != &thrd_pool->head->job &&
       !atomic_compare_exchange_weak(&thrd_pool->head->prev, &job,
                                     job->prev)) {
}
```

, keeps trying to claim the job atomically until it succeeds.
A failed compare-exchange writes the current value back into `job`,
so the guard is re-evaluated on every iteration:
another worker may have taken the last job in the meantime,
leaving the idle job, which must never be claimed.

Built-in post increment and decrement operators and compound assignment on atomic objects, such as `++` and `+=`, are read-modify-write atomic operations with total sequentially consistent ordering as well.
They behave equivalently to a `do while` loop. See C11 standard 6.5.2.4 and 6.5.16.2 for more details.

What if claiming a job, which updates `thrd_pool->head->prev`, is not done atomically?
Two or more threads could have races updating `thrd_pool->head->prev` and working on the same job.
Data races are undefined behavior in C11 and C++11.
Working on the same job can lead to duplication of the calculation of `job->future->result`,
use after free and double free on the job.

But even when jobs are claimed atomically, a thread can still end up holding a job that has been freed.
This is a defect of the example code.
Jobs in the example are dynamically allocated. They are freed after a worker finishes each job.
However, this situation may lead to dangling pointers for workers that are still holding and attempting to claim the job.
If jobs are intended to be dynamically allocated, then safe memory reclamation should be implemented for such shared objects.
RCU, hazard pointers, and reference counting are major ways of solving this problem.
