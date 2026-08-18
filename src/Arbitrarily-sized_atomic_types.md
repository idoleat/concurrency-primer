# Arbitrarily-sized "atomic" types

Along with `atomic_int` and friends,
C++ provides the template `std::atomic<T>` for defining arbitrary atomic types.
C, lacking a similar language feature but wanting to provide the same functionality,
added an `_Atomic` keyword.
If `T` is larger than the machine's word size,
the compiler and the language runtime automatically surround the variable's reads and writes with locks.
If you want to make sure this is not happening,[^1]
you can check with:

```cpp
std::atomic<Foo> bar;
ASSERT(bar.is_lock_free());
```

In most cases,[^2]
this information is known at compile time.
Consequently, C++17 added `is_always_lock_free`:

```cpp
static_assert(std::atomic<Foo>::is_always_lock_free);
```

[^1]: ...which is most of the time,
    since we are usually using atomic operations to avoid locks in the first place.

[^2]: The language standards permit atomic types to be *sometimes* lock-free.
    This might be necessary for architectures that do not guarantee atomicity for unaligned reads and writes.
