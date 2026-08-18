# Concurrency tools and synchronization mechanisms

Atomic loads, stores, and <small>RMW</small> operations are the building blocks for every single concurrency tool.
It is useful to split those tools into two camps:
*blocking* and *lockless*.

As mentioned in [Read-modify-write](./read-modify-write.html), multiple threads can use these blocking tools to communicate with others.
Furthermore, these blocking tools can even assist in synchronization between threads.
The blocking mechanism is quite simple,
because all threads need to do is block others in order to make their own progress.
However, this simplicity can also cause threads to pause for unpredictable durations and then influence the progress of the overall system.

Take a mutex as an example:
it requires threads to access shared data sequentially.
If a thread locks the mutex and another attempts to lock it too,
the second thread must wait, or *block*,
until the first one unlocks it, regardless of the wait time.
Additionally, blocking mechanisms are prone to *deadlock* and *livelock*,
issues that lead to the system becoming immobilized as threads perpetually wait on each other.

If the first thread acquires a mutex first,
then the second thread locks another mutex and subsequently attempts to lock the mutex held by the first thread.
At the same time, the first thread also tries to lock the mutex held by the second thread.
Then the deadlock occurs.
Therefore, we can see that deadlock occurs when different threads acquire locks in incompatible orders,
leading to system immobilization as threads perpetually wait on each other.

Additionally, in [Shared Resources](./shared_resources.html),
we can see another problem with the lock: its scalability is limited.

After understanding the issue that blocking mechanisms are prone to,
we try to achieve synchronization between threads without lock.
Consider the program below: if there is only a single thread, execute these operations as follows:

```cpp
while (x == 0)
    x = 1 - x;
```

When executed by a single thread, these operations complete within a finite time.
However, with two threads executing concurrently,
if one thread executes `x = 1 - x` and the other thread executes `x = 1 - x` subsequently,
then the value of x will always be 0, which will lead to a livelock.
Therefore, even without any locks in concurrent threads,
we still cannot guarantee that the overall system can make progress toward achieving the programmer's goals.

Consequently, we should not focus on comparing which communication tools or synchronization mechanisms are better,
but rather on exploring how to effectively use these tools in a given scenario to facilitate smooth communication between threads and achieve the programmer's goals.
