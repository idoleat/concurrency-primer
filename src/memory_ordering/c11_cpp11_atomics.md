# C11/C++11 atomics

By default, all atomic operations, including loads, stores, and various forms of <small>RMW</small>,
are considered sequentially consistent.
However, this is just one among many possible orderings.
We will explore each of these orderings in detail.
A comprehensive list, as well as the corresponding enumerations used by the C and C++ <small>API</small>, can be found here:
-   Sequentially Consistent (`memory_order_seq_cst`)
-   Acquire (`memory_order_acquire`)
-   Release (`memory_order_release`)
-   Relaxed (`memory_order_relaxed`)
-   Acquire-Release (`memory_order_acq_rel`)
-   Consume (`memory_order_consume`)

To pick an ordering,
you provide it as an optional argument that we have slyly failed to mention so far:[^1]

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

[^1]: In C, separate functions are defined for cases where specifying an ordering is necessary.
    `exchange()` becomes `exchange_explicit()`, a <small>CAS</small>
    becomes `compare_exchange_strong_explicit()`, and so on.

## Acquire and release

We have just examined the acquire and release operations in the context of the lock example from [Do we always need sequentially consistent operations?](../do_we_always_need_seq-cst.html).
You can think of them as "one-way" barriers: an acquire operation permits other reads and writes to move past it,
but only in a \\(before \to after\\) direction.
A release works the opposite manner, allowing actions to move in an \\(after \to before\\) direction.
On <small>ARM</small> and other weakly-ordered architectures, this enables us to eliminate one of the memory barriers in each operation,
such that

```cpp
int acquireFoo()
{
    return foo.load(memory_order_acquire);
}

void releaseFoo(int i)
{
    foo.store(i, memory_order_release);
}
```

become:

:::horizontal
```armasm
acquireFoo:
  ldr r3, <&foo>
  ldr r0, [r3, #0]
  dmb
  bx lr
```

```armasm
releaseFoo:
  ldr r3, <&foo>
  dmb
  str r0, [r3, #0]
  bx lr
```
:::

Together, these provide \\(writer \to reader\\) synchronization:
if thread *W* stores a value with release semantics,
and thread *R* loads that value with acquire semantics,
then all writes made by *W* before its store-release are observable to *R* after its load-acquire.
If this sounds familiar, it is exactly what we were trying to achieve in
[Background](../background.html) and [Enforcing law and order](../enforcing_law_and_order.html):

```cpp
int v;
std::atomic_bool v_ready(false);

void threadA()
{
    v = 42;
    v_ready.store(true, memory_order_release);
}

void threadB()
{
    while (!v_ready.load(memory_order_acquire)) {
        // wait
    }
    assert(v == 42); // Must be true
}
```

## Relaxed

Relaxed atomic operations are useful for variables shared between threads where *no specific order* of operations is needed.
Although it may seem like a niche requirement, such scenarios are quite common.

Relaxed operations are beneficial for managing flags shared between threads.
For example, a worker thread in thread pool in [Read-modify-write](../read-modify-write.html) might continuously run until it receives a cancelled signal:

```c
while (1) {
    if (atomic_load_explicit(&thrd_pool->state, memory_order_relaxed) == cancelled)
        return EXIT_SUCCESS;
    /* acquire: unlike cancelled, this one announces a filled queue */
    if (atomic_load_explicit(&thrd_pool->state, memory_order_acquire) == running) {
        /* claim the job */
        job_t *job = atomic_load_explicit(&thrd_pool->head->prev,
                                          memory_order_acquire);
        while (job != &thrd_pool->head->job &&
               !atomic_compare_exchange_weak_explicit(&thrd_pool->head->prev,
                                                      &job, job->prev,
                                                      memory_order_release,
                                                      memory_order_acquire))
            ;
        if (job == &thrd_pool->head->job) {
            atomic_store(&thrd_pool->state, idle);
            thrd_yield();
        } else {
            job->future->result = job->func(job->future->arg);
            atomic_flag_clear(&job->future->flag);
            free(job); /* could cause dangling pointer in other threads */
        }
    } else {
        thrd_yield();
    }
}
```

We do not care if the contents of the loop are rearranged around that load.
Nothing bad will happen so long as `cancelled` is only used to tell the worker to exit, and not to "announce" any new data.
The very next line shows where that condition stops holding.
`running` does announce data, because the employer fills the queue and only then switches the pool to it,
so that load is an acquire and pairs with the employer's store.
Everything the employer wrote beforehand, including the links it rewrote on jobs that were already queued, is ordered by that one pairing.
It is the whole reason the worker may then walk the queue at all,
and it holds only for as long as the employer confines its edits to a pool that is idle.

Finally, relaxed loads are commonly used with <small>CAS</small> loops,
where a failed comparison means nothing more than "try again"
and no order needs enforcing until we have successfully modified our value.
The loop above is not one of those cases, which is why both of the reads it makes on `head->prev` are acquires:
it follows the pointer it reads, taking `job->prev` to compute the next candidate and dereferencing the job once the claim succeeds.
A release on the successful <small>CAS</small> only keeps the claiming thread's own earlier work from drifting past it;
it constrains nothing that comes afterwards,
so it cannot make the employer's writes visible to the reads that follow the claim.
That has to come from the reading side, and there are two reads here, both of which need it:
the initial load, and the reload that a failed compare-exchange performs, which is why the failure order is an acquire rather than relaxed.
A <small>CAS</small> loop that only re-reads a value it never follows can leave every load relaxed.

## Acquire-Release

`memory_order_acq_rel` is used with atomic <small>RMW</small> operations that need to both load-acquire *and* store-release a value.
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

1.  All access to the referenced object happens *before* the count reaches zero.
2.  Deletion happens *after* the reference count reaches zero.[^2]

Curious readers might be wondering about the difference between acquire-release and sequentially consistent operations.
To quote Hans Boehm, chair of the ISO C++ Concurrency Study Group,

> The difference between `acq_rel` and `seq_cst` is generally whether the operation is required to participate in the single global order of sequentially consistent operations.

In other words, acquire-release provides order relative to the variable being load-acquired and store-released,
whereas sequentially consistent operation provides some *global* order across the entire program.
If the distinction still seems hazy, you are not alone.
Boehm goes on to say,

> This has subtle and unintuitive effects.
> The \[barriers\] in the current standard may be the most
> experts-only construct we have in the language.

[^2]: This can be optimized even further by making the acquire barrier only occur conditionally,
    when the reference count is zero.
    Standalone barriers are outside the scope of this paper,
    since they are almost always pessimal compared to a combined load-acquire or store-release.

## Consume

Last but not least, we introduce `memory_order_consume`.
Imagine a situation where data changes rarely but is frequently read by many threads.
For example, in a kernel tracking peripherals connected to a machine,
updates to this information occur very infrequently---only when a device is plugged in or removed.
In such cases, it is logical to prioritize read optimization as much as possible.
Based on our current understanding, the most effective strategy is:

```cpp
std::atomic<PeripheralData*> peripherals;

// Writers:
PeripheralData* p = kAllocate(sizeof(*p));
populateWithNewDeviceData(p);
peripherals.store(p, memory_order_release);
```

```cpp
// Readers:
PeripheralData *p = peripherals.load(memory_order_acquire);
if (p != nullptr) {
    doSomethingWith(p->keyboards);
}
```

To further enhance optimization for readers,
bypassing a memory barrier on weakly-ordered systems for loads would be ideal.
Fortunately, this is often achievable.
The data being accessed (`p->keyboards`) relies on the value of `p`,
leading most platforms, including those with weak ordering,
to maintain the sequence of the initial load (`p = peripherals`) and its subsequent use (`p->keyboards`).
However, it is notable that on some particularly weakly-ordered architectures, like DEC Alpha,
this reordering can occur, much to the frustration of developers.
Ensuring the compiler avoids any similar reordering is crucial, and `memory_order_consume` is designed for this purpose.
Change readers to:

```cpp
PeripheralData *p = peripherals.load(memory_order_consume);
if (p != nullptr) {
    doSomethingWith(p->keyboards);
}
```

and an <small>ARM</small> compiler could emit:

```armasm
  ldr r3, &peripherals
  ldr r3, [r3]
  // Look ma, no barrier!
  cbz r3, was_null // Check for null
  ldr r0, [r3, #4] // Load p->keyboards
  b doSomethingWith(Keyboards*)
was_null:
  ...
```

Sadly, the emphasis here is on *could*.
Figuring out what constitutes a "dependency" between expressions is not as trivial as one might hope,[^3]
so all compilers currently convert consume operations to acquires.

[^3]: Even the experts in
    the <small>ISO</small> committee's concurrency study group, <small>SG</small>1,
    came away with different understandings.
    See
    [<small>N</small>4036](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n4036.pdf)
    for the gory details.
    Proposed solutions are explored in
    [<small>P</small>0190<small>R</small>3](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0190r3.pdf)
    and
    [<small>P</small>0462<small>R</small>1](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0462r1.pdf).
