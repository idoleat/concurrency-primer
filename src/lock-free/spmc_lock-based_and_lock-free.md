# SPMC solution - lock-based and lock-free

As described in [SPMC solution - lock-based](./spmc_lock-based.html), there is a problem when the producer suspends;
the whole system cannot make any progress.
Additionally, consumers contend for the lock of the job queue to access the job;
however, after they acquire the lock, they may still need to wait when the queue is empty.
To solve this issue, this section introduces lock-based and lock-free algorithms.

The following text explains the meaning of each state in [the figure](#fig:spmc-solution2).

**state 0** : The producer prepares all the jobs in advance.

**state 1** : Consumer 1 acquires the lock on the job queue, takes a job, and releases the lock.

**state 2** : After consumer 2 acquires the lock, it definitely can find that there are still jobs in the queue.

Through this approach, once a consumer obtains the lock on the job queue,
there is guaranteed to be a job available unless all jobs have been taken by other consumers.
Thus, there is no need to wait due to a lack of jobs;
the only wait is for acquiring the lock to access the job queue.

<a id="fig:spmc-solution2"></a>
<!-- IMAGE PLACEHOLDER: images/spmc-solution2 -->

> *The interaction between the producer and consumer in Solution 2,
> including their state transitions.*

This implementation is referred to as both lock-based and lock-free.
The algorithm is designed such that the producer adds all jobs to the job queue before multiple consumers begin taking them.
This design ensures that if the producer suspends or adds jobs slowly,
consumers will not be blocked due to the lack of a job.
Consumers simply think they have completed all the jobs that the producer added.
Therefore, this implementation qualifies as lock-free, as shown in [the figure](./type_of_progress.html#fig:progress-type).
The reason that the implementation of getting a job is lock-based, not lock-free,
is the same as the second reason described in [SPMC solution - lock-based](./spmc_lock-based.html).
