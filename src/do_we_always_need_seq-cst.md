# Do we always need sequentially consistent operations?

All of our examples so far have been sequentially consistent to prevent reorderings that break our code.
We have also seen how weakly-ordered architectures like <small>Arm</small> use memory barriers to create sequential consistency.
But as you might expect, these barriers can have a noticeable impact on performance.
After all, they inhibit optimizations that your compiler and hardware would otherwise make.

What if we could avoid some of this slowdown?
Consider a simple case like the spinlock from [test and set](./read-modify-write/test_and_set.html#test-and-set).
Between the `lock()` and `unlock()` calls, we have a *critical section* where we can safely modify shared state protected by the lock.
Outside this critical section, we only read and write to things that are not shared with other threads.
```cpp
deepThought.calculate(); // non-shared

lock(); // Lock; critical section begins
sharedState.subject = "Life, the universe and everything";
sharedState.answer = 42;
unlock(); // Unlock; critical section ends

demolishEarth(vogons); // non-shared
```
It is vital that reads and writes to shared memory do not move outside the critical section.
But the opposite is not true!
The compiler and hardware could move as much as they want *into* the critical section without causing any trouble.
We have no problem with the following if it is somehow faster:
```cpp
lock(); // Lock; critical section begins
deepThought.calculate(); // non-shared
sharedState.subject = "Life, the universe and everything";
sharedState.answer = 42;
demolishEarth(vogons); // non-shared
unlock(); // Unlock; critical section ends
```
So, how do we tell the compiler as much?
