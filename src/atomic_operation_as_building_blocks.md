# Atomic operations as building blocks

Atomic loads, stores, and <small>RMW</small> operations are the building blocks for every single concurrency tool.
It is useful to split those tools into two camps: *blocking* and *lockless*.

Blocking synchronization methods are generally easier to understand,
but they can cause threads to pause for unpredictable durations.
Take a mutex as an example:
it requires threads to access shared data sequentially.
If a thread locks the mutex and another attempts to lock it too,
the second thread must wait, or *block*,
until the first one unlocks it, regardless of the wait time.
Additionally, blocking mechanisms are prone to *deadlock* and *livelock*,
issues that lead to the system becoming immobilized as threads perpetually wait on each other.

In contrast, lockless synchronization methods ensure that the program is always making forward progress.
These are *non-blocking* since no thread can cause another to wait indefinitely.
Consider a program that streams audio,
or an embedded system where a sensor triggers an interrupt service routine (<small>ISR</small>) when new data arrives.
We want lock-free algorithms and data structures in these situations,
since blocking could break them.
(In the first case, the user's audio will begin to stutter if sound data is not provided at the bitrate it is consumed.
In the second, subsequent sensor inputs could be missed if the <small>ISR</small> does not complete as quickly as possible.)

Lockless algorithms are not inherently superior or quicker than blocking ones;
they serve different purposes with their own design philosophies.
Additionally, the mere use of atomic operations does not render algorithms lock-free.
For example, our basic spinlock discussed in [test and set](/read-modify-write/test_and_set.html#test-and-set) is still considered a blocking algorithm even though it eschews <small>OS</small>-specific syscalls for making the blocked thread sleep.
Putting a blocked thread to sleep is often an optimization,
allowing the operating system's scheduler to allocate <small>CPU</small> resources to active threads until the blocked one is revived.
Some concurrency libraries even introduce hybrid locks that combine brief spinning with sleeping to balance <small>CPU</small> usage and context-switching overheads.

Both blocking and lockless approaches have their place in software development.
When performance is a key consideration, it is crucial to profile your application.
The performance impact varies with numerous factors, such as thread count and <small>CPU</small> architecture specifics.
Balancing complexity and performance is essential in concurrency, a domain fraught with challenges.
