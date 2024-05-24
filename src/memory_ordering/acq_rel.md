# Acquire-Release

`memory_order_acq_rel` is used with atomic RMW operations that need to both load-acquire *and* store-release a value.
A typical example involves thread-safe reference counting,
like in C++'s `shared_ptr`:
```cpp
atomic_int refCount;

void inc()
{
    refCount.fetch_add(1, memory_order_relaxed);
}
```
```cpp
void dec()
{
    if (refCount.fetch_sub(1, memory_order_acq_rel) == 1) {
        // No more references, delete the data.
    }
}
```

Order does not matter when incrementing the reference count since no action is taken as a result.
However, when we decrement, we must ensure that:
1. All access to the referenced object happens *before* the count reaches zero.
2. Deletion happens *after* the reference count reaches zero.[^a]

Curious readers might be wondering about the difference between acquire-release and sequentially consistent operations.
To quote Hans Boehm, chair of the ISO C++ Concurrency Study Group,
> The difference between `acq_rel` and `seq_cst` is generally whether the operation is required to participate in the single global order of sequentially consistent operations.

In other words, acquire-release provides order relative to the variable being load-acquired and store-released,
whereas sequentially consistent operation provides some *global* order across the entire program.
If the distinction still seems hazy, you are not alone.
Boehm goes on to say,
> This has subtle and unintuitive effects.
> The [barriers] in the current standard may be the most
> experts-only construct we have in the language.

[^a]: This can be optimized even further by making the acquire barrier only occur conditionally,
when the reference count is zero.
Standalone barriers are outside the scope of this paper,
since they are almost always pessimal compared to a combined load-acquire or store-release.
