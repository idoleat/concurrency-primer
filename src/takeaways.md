# Takeaways

We have only scratched the surface here, but hopefully you now know:
- Why compilers and <small>CPU</small> hardware reorder loads and stores.
- Why we need special tools to prevent these reorderings to communicate between threads.
- How we can guarantee *sequential consistency* in our programs.
- Atomic *read-modify-write* operations.
- How atomic operations can be implemented on weakly-ordered hardware, and what implications this can have for a language-level <small>API</small>.
- How we can *carefully* optimize lockless code using non-sequentially-consistent memory orderings.
- How *false sharing* can impact the performance of concurrent memory access.
- Why `volatile` is an inappropriate tool for inter-thread communication.
- How to prevent the compiler from fusing atomic operations in undesirable ways.

To learn more, see the additional resources below,
or examine lock-free data structures and algorithms,
such as a *single-producer/single-consumer* (<small>SP/SC</small>) queue or *read-copy-update*
(<small>RCU</small>).[^a]

Good luck and godspeed!

[^a]: See the LWN article, [What is RCU, Fundamentally?](https://lwn.net/Articles/262464/) for an introduction.
