# SPMC solution - lock-based

First, we introduce the scenario of lock-based algorithms.
At any time, there is only one consumer that can get the lock to access the job queue.
This is because in this scenario, the lock is a mutex lock, also known as a mutual-exclusion lock.
Until the consumer releases the lock, the other consumers are blocked when attempting to access the job queue.

The following text explains the meaning of each state in [the figure](#fig:spmc-solution1).

**state 1** : The producer is adding tasks to the job queue while multiple consumers wait for tasks to become available and are ready to take on any job that appears in the job queue.

**state 2** \\(\to\\) **state 3** : After the producer adds a task to the job queue,
the producer releases the mutex lock, and then wakes up the consumers.
Those consumers had previously tried to acquire the job queue lock.

**state 3** \\(\to\\) **state 4** : Consumer 1 acquires the mutex lock for the job queue,
retrieves a task from it, and then releases the mutex lock.

**state 5** : Next, other consumers attempt to acquire the mutex lock for the job queue.
However, after they acquire the lock, they find no tasks in the queue.
This is because the producer has not added more tasks to the job queue.

**state 6** : Consequently, the consumers wait on a condition variable.
During this time, the consumers are not busy waiting but rather waiting for the producer to wake them up.
This is because the mechanism is an advanced form of a mutex lock.

<a id="fig:spmc-solution1"></a>
<!-- IMAGE PLACEHOLDER: images/spmc-solution1 -->

> *The interaction between the producer and consumer in SPMC Solution 1,
> including their state transitions.*

The reason why this implementation is not lock-free is:
First, if a producer suspends,
it causes consumers to have no job available,
leading them to block and thus halting progress in the entire system,
which is obstruction-free, as shown in [the figure](./type_of_progress.html#fig:progress-type).
Second, consumers need to concurrently access a shared resource: the job.
Then, one consumer acquires the lock of the job queue but suddenly gets suspended before completing without unlocking,
causing other consumers to be blocked.
Meanwhile, the producer still keeps adding jobs, but the system fails to make any progress,
which is obstruction-free, as shown in [the figure](./type_of_progress.html#fig:progress-type).
Therefore, neither the former nor the latter implementation approach is lock-free.
