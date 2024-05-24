# Consume

Last but not least, we introduce `memory_order_consume`.
Imagine a situation where data changes rarely but is frequently read by many threads.
For example, in a kernel tracking peripherals connected to a machine,
updates to this information occur very infrequently—only when a device is plugged in or removed.
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
and an ARM compiler could emit:
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
Figuring out what constitutes a "dependency" between expressions is not as trivial as one might hope,[^a]
so all compilers currently convert consume operations to acquires.

[^a]: Even the experts in
the <small>ISO</small> committee's concurrency study group, <small>SG</small>1,
came away with different understandings.
See
[<small>N</small>4036](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n4036.pdf)
for the gory details.
Proposed solutions are explored in
[<small>P</small>0190<small>R</small>3](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0190r3.pdf)
and
[<small>P</small>0462<small>R</small>1](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0462r1.pdf).
