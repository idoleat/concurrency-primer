# Type of progress

When we consider the scenario where many concurrent threads collaborate and each thread is divided into many operations,

**Wait-Free** Every operation in every thread will be completed within a limited time.
This also implies that each operation contributes to the overall progress of the system.

**Lock-Free** At any given moment, among all operations in every thread,
at least one operation contributes to the overall progress of the system.
However, it does not guarantee that starvation will not occur.

**Obstruction-Free** At any given time, if there is only a single thread operating without interference from other threads,
its instructions can be completed within a finite time. However, when threads are working concurrently,
it does not guarantee progress.

Therefore, we can understand their three relationships as follows:
obstruction-free includes lock-free and lock-free includes wait-free.
Achieving wait-free is the most optimal approach,
allowing each thread to make progress without being blocked by other threads.

<a id="fig:progress-type"></a>
{{#include ../../images/progress-type.svg}}
> *In a wait-free system, each thread is guaranteed to make progress at every moment because no thread can block others.
> This ensures that the overall system can always make progress.
> In a lock-free system, at Time 1, Thread 1 may cause other threads to wait while it performs its operation.
> However, even if Thread 1 suspends at Time 2, it does not subsequently block other threads.
> This allows Thread 2 to make progress at Time 3, ensuring that the overall system continues to make progress even if one thread is suspended.
> In an obstruction-free system, when Thread 1 is suspended at Time 2,
> it causes other threads to be blocked as a result. This means that by Time 3,
> Thread 2 and Thread 3 are still waiting, preventing the system from making progress thereafter.
> Therefore, obstruction-free systems may halt progress if one thread is suspended,
> leading to the potential blocking of other threads and even stalling the system.*

The main goal is that the whole system,
which contains all concurrent threads,
is always making forward progress.
To achieve this goal, we rely on concurrency tools,
including atomic operations and operations that behave atomically, as described in [Read-modify-write](../read-modify-write.html).
Additionally, we carefully select synchronization mechanisms, as described in [Concurrency tools and synchronization mechanisms](../concurrency_tools.html),
which may involve utilizing shared resources for communication (e.g., spinlock), as described in [Shared Resources](../shared_resources.html).
Furthermore, we design our program with appropriate data structures and algorithms.
Therefore, lock-free doesn't mean we cannot use any lock;
we just need to ensure that the blocking mechanism will not limit the scalability and that the system can avoid the problems described in [Concurrency tools and synchronization mechanisms](../concurrency_tools.html) (e.g., long waits, deadlock).

Next, we take the single producer and multiple consumers problem as an example to demonstrate how to achieve fully lock-free programming by improving some implementations step by step.[^1]
This problem is that one producer generates tasks and adds them to a job queue,
and multiple consumers take tasks from the job queue and execute them.

[^1]: The first three solutions, which are [SPMC solution - lock-based](./spmc_lock-based.html), [SPMC solution - lock-based and lock-free](./spmc_lock-based_and_lock-free.html), and [SPMC solution - fully lock-free](./spmc_fully_lock-free.html), are based on Herb Sutter's
    [talk from CppCon 2014.](https://youtu.be/c1gO9aB9nbs?si=7qJs-0qZAVqLHr1P)
