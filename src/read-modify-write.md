# Read-modify-write

So far we have introduced the importance of order and atomicity.
In [Enforcing law and order](./enforcing_law_and_order.html), we see how an atomic object ensures the order of a single store or load operation is not reordered by the compiler within a program.
Only upon establishing the correct inter-thread order can we continue to pursue how multiple threads can establish a correct cross-thread order.
After achieving this goal, we can further explore how concurrent threads can coordinate and collaborate smoothly.
In [Atomicity](./atomicity.html), there is a need for atomicity to ensure that a group of operations is not only sequentially executed but also completes without being interrupted by operations from other threads.
This establishes the correct order of operations from different threads.

<a id="fig:atomic-rmw"></a>
<!-- IMAGE PLACEHOLDER: images/atomic-rmw -->

> *Exchange, Test and Set, Fetch and..., Compare and Swap can all be transformed into atomic RMW operations, ensuring that operations like \\(t1 \to t2 \to t3\\) will become an atomic step.*

Atomic loads and stores are all well and good when we do not need to consider the previous state of atomic variables, but sometimes we need to read a value, modify it, and write it back as a single atomic step.
As shown in [the figure](#fig:atomic-rmw), the modification is based on the previous state that is visible for reading, and the result is then written back.
A complete *read-modify-write* operation is performed atomically to ensure visibility to subsequent operations.

Furthermore, for communication between concurrent threads, a shared resource is required, as shown in [the figure](./atomicity.html#fig:atomicity).
Think back to the discussion in previous sections.
In order for concurrent threads to collaborate on operating a shared resource, we need a way to communicate.
Thus, the need for a channel for communication arises with the appearance of the shared resource.

As discussed earlier, the process of accessing shared resources responsible for communication must also ensure both order and non-interference.
To prevent the recursive protection of shared resources,
atomic operations can be introduced for the shared resources responsible for communication, as shown in [the figure](#fig:atomic-types).

There are a few common *read-modify-write* (<small>RMW</small>) operations that turn a read, a modification, and a write into a single atomic step.
In C++, they are represented as member functions of `std::atomic<T>`.
In C, they are freestanding functions.

<a id="fig:atomic-types"></a>
<!-- IMAGE PLACEHOLDER: images/atomic-types -->

> *Test and Set (Left) and Compare and Swap (Right) leverage their functionality of checking and their atomicity to make other RMW operations perform atomically.
> The red color represents atomic RMW operations, while the blue color represents RMW operations that behave atomically.*
