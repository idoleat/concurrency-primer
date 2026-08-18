# Shared Resources

From [Read-modify-write](./read-modify-write.html), we have understood that there are two types of shared resources that need to be considered.
The first type is shared resources that concurrent threads will access in order to collaborate to achieve a goal.
The second type is shared resources that serve as a communication channel for concurrent threads,
ensuring correct access to shared resources.
However, all of these considerations stem from a programming perspective,
where we only distinguish between shared resources and private resources.

Given all the complexities to consider, modern hardware adds another layer to the puzzle,
as depicted in [the figure](./background.html#fig:dunnington).
Remember, memory moves between the main <small>RAM</small> and the <small>CPU</small> in segments known as cache lines.
These cache lines also represent the smallest unit of data transferred between cores and caches.
When one core writes a value and another reads it,
the entire cache line containing that value must be transferred from the first core's cache(s) to the second core's cache(s),
ensuring a coherent "view" of memory across cores. This dynamic can significantly affect performance.

This slowdown is even more insidious when it occurs between unrelated variables that happen to be placed on the same shared resource,
which is the cache line, as shown in [the figure](#fig:false-sharing).
When designing concurrent data structures or algorithms,
this *false sharing* must be taken into account.
One way to avoid it is to pad atomic variables with a cache line of private data,
but this is obviously a large space-time trade-off.

<a id="fig:false-sharing"></a>
<!-- IMAGE PLACEHOLDER: images/false-sharing -->

> *Processor 1 and Processor 2 operate independently on variables A and B.
> Simultaneously, they read the cache line containing these two variables.
> In the next time step, each processor modifies A and B in their private L1 cache separately.
> Subsequently, both processors write their modified cache line to the shared L2 cache.
> At this moment, the expansion of the scope of shared resources to encompass cache lines highlights the importance of considering cache coherence issues.*

Not only shared resources,
but we also need to consider shared resources that serve as a communication channel, e.g. spinlock (see [Test and set](./read-modify-write/test_and_set.html#spinlock)).
Processors using locks as a communication channel also need to transfer the cache line.
When a processor broadcasts the release of a lock,
multiple processors on different chips attempt to acquire the lock simultaneously.
To ensure a consistent state of the lock across all private L1 cache lines,
which is a part of cache coherence,
the cache line containing the lock will be continually transferred among the caches of those cores.
Unless the critical sections are considerably lengthy,
the time spent managing this cache line movement could exceed the time spent within the critical sections themselves,[^1]
despite the algorithm's non-blocking nature.

With these high communication costs, there may be only one processor that succeeds in acquiring it again in the case of mutex lock or spinlock, as shown in [the figure](#fig:spinlock).
Then the other processors that have not successfully acquired the lock will continue to wait,
resulting in little practical benefit (only one processor gains the lock) and significant communication overhead.
This disparity severely limits the scalability of the spin lock.

<a id="fig:spinlock"></a>
<!-- IMAGE PLACEHOLDER: images/spinlock -->

> *Three processors use a lock as a communication channel to ensure correct access to the shared L2 cache.
> Processors 2 and 3 are trying to acquire a lock that is held by processor 1.
> Therefore, when processor 1 unlocks,
> the state of the lock needs to be updated in the other processors' private L1 caches.*

[^1]: This situation underlines how some systems may experience a cache miss that is substantially more costly than an atomic <small>RMW</small> operation,
    as discussed in Paul E. McKenney's
    [talk from CppCon 2017](https://www.youtube.com/watch?v=74QjNwYAJ7M)
    for a deeper exploration.
