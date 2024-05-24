# Memory orderings

By default, all atomic operations, including loads, stores, and various forms of <small>RMW</small>,
are considered sequentially consistent.
However, this is just one among many possible orderings.
We will explore each of these orderings in detail.
A comprehensive list, as well as the corresponding enumerations used by the C and C++ <small>API</small>, can be found here:
- Sequentially Consistent (`memory_order_seq_cst`)
- Acquire (`memory_order_acquire`)
- Release (`memory_order_release`)
- Relaxed (`memory_order_relaxed`)
- Acquire-Release (`memory_order_acq_rel`)
- Consume (`memory_order_consume`)

To pick an ordering,
you provide it as an optional argument that we have slyly failed to mention so far:[^a]
```cpp
void lock()
{
    while (af.test_and_set(memory_order_acquire)) { /* wait */ }
}

void unlock()
{
    af.clear(memory_order_release);
}
```
Non-sequentially consistent loads and stores also use member functions of `std::atomic<>`:
```cpp
int i = foo.load(memory_order_acquire);
```
Compare-and-swap operations are a bit odd in that they have *two* orderings: one for when the <small>CAS</small> succeeds, and one for when it fails:
```cpp
while (!foo.compare_exchange_weak(
    expected, expected * by,
    memory_order_seq_cst, // On success
    memory_order_relaxed)) // On failure
    { /* empty loop */ }
```

With the syntax out of the way,
let's look at what these orderings are and how we can use them.
As it turns out, almost all of the examples we have seen so far do not actually need sequentially consistent operations.

[^a]: In C, separate functions are defined for cases where specifying an ordering is necessary.
`exchange()` becomes `exchange_explicit()`, a <small>CAS</small>
becomes `compare_exchange_strong_explicit()`, and so on.
