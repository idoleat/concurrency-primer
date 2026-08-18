# SPMC solution - fully lock-free

As described in [Shared Resources](../shared_resources.html),
we can understand that communications between processors across a chip are through cache lines,
which incurs high costs. Additionally, using locks further decreases overall performance and limits scalability.
However, when locks are necessary for concurrent threads to communicate,
reducing the amount of shared state and the granularity of the shared resource used for communication (e.g., spinlock, mutex lock) is crucial.
Therefore, to achieve fully lock-free programming, we change the data structure to reduce the granularity of locks.

<a id="fig:spmc-solution3"></a>
{{#include ../../images/spmc-solution3.svg}}
> *The left side shows that the lock protects the entire job queue to ensure exclusive access to its head for multiple threads.
> The right side illustrates that each thread has its own slot for accessing jobs,
> not only achieving exclusivity through data structure but also eliminating the need for shared resources for communication.*

Providing each consumer with their own unique slot to access jobs addresses the problem at its root,
directly avoiding competition.
By doing so, consumers no longer rely on a shared resource for communication.
Consequently, other consumers will not be blocked by a suspended consumer holding a lock.
This approach ensures that the system maintains its progress,
as each consumer operates independently within their own slot,
which is lock-free, as shown in [the figure](./type_of_progress.html#fig:progress-type).
