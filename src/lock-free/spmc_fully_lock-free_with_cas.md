# SPMC solution - fully lock-free with CAS

In addition to reducing granularity,
there is another way to avoid the situation where one consumer acquires the lock on the job queue, gets suspended, and blocks other consumers, as described in [SPMC solution - lock-based and lock-free](./spmc_lock-based_and_lock-free.html).
As described in [Compare and swap](../read-modify-write/compare_and_swap.html), we can use <small>CAS</small> with a loop to ensure that the write operation achieves semantic atomicity.

Unlike [SPMC solution - lock-based and lock-free](./spmc_lock-based_and_lock-free.html),
which uses a shared resource (e.g., an advanced form of a mutex lock) for blocking synchronization,
the first thread holding the lock causes the other threads to wait until the first thread releases the lock.
As described in [Compare and swap](../read-modify-write/compare_and_swap.html), <small>CAS</small> allows threads that initially failed to acquire the lock to continue to execute Read and Modify.
Therefore, we can conclude that if one thread is blocked,
it indicates that another thread is making progress,
which is lock-free, as shown in [the figure](./type_of_progress.html#fig:progress-type).

As described in [SPMC solution - lock-based and lock-free](./spmc_lock-based_and_lock-free.html), a blocking mechanism uses a mutex lock;
we can see that only one thread is active when it accesses the job queue.
Although <small>CAS</small> will continue to execute Read and Modify,
it doesn't result in an increase in overall progress.
This is because the operations will be useless when atomic <small>CAS</small> fails.
Therefore, we can understand that lock-free algorithms are not faster than blocking ones.
The reason for using lock-free is to ensure that if one thread is blocked,
it doesn't cause other threads to be blocked,
thereby ensuring that the overall system must make progress over a long period of time.
