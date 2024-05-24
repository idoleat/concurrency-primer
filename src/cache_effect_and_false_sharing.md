# Cache effects and false sharing

Given all the complexities to consider, modern hardware adds another layer to the puzzle.
Remember, memory moves between main <small>RAM</small> and the <small>CPU</small> in segments known as cache lines.
These lines also represent the smallest unit of data transferred between cores and their caches.
When one core writes a value and another reads it,
the entire cache line containing that value must be transferred from the first core's cache(s) to the second,
ensuring a coherent "view" of memory across cores.

This dynamic can significantly affect performance.
Take a readers-writer lock, for example,
which prevents data races by allowing either a single writer or multiple readers access to shared data but not simultaneously.
At its most basic, this concept can be summarized as follows:
```cpp
struct RWLock {
    int readers;
    bool hasWriter; // Zero or one writers
};
```
Writers must wait until the `readers` count drops to zero,
while readers can acquire the lock through an atomic <small>RMW</small> operation if `hasWriter` is `false`.

At first glance, this approach might seem significantly more efficient than exclusive locking mechanisms (e.g., mutexes or spinlocks) in scenarios where shared data is read more frequently than written.
However, this perspective overlooks the impact of cache coherence.
If multiple readers on different cores attempt to acquire the lock simultaneously,
the cache line containing the lock will constantly be transferred among the caches of those cores.
Unless the critical sections are considerably lengthy,
the time spent managing this cache line movement could exceed the time spent within the critical sections themselves,[^a]
despite the algorithm's non-blocking nature.

This slowdown is even more insidious when it occurs between unrelated variables that happen to be placed on the same cache line.
When designing concurrent data structures or algorithms,
this *false sharing* must be taken into account.
One way to avoid it is to pad atomic variables with a cache line of unshared data, but this is obviously a large space-time tradeoff.

[^a]: This situation underlines how some systems may experience a cache miss that is substantially more costly than an atomic <small>RMW</small> operation,
as discussed in Paul E. McKenney's
[talk from CppCon 2017](https://www.youtube.com/watch?v=74QjNwYAJ7M)
for a deeper exploration.
