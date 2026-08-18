# Atomicity

But order is only one of the vital ingredients for inter-thread communication.
The other is what atomic types are named for: atomicity.
Something is *atomic* if it can not be divided into smaller parts.
If threads do not use atomic reads and writes to share data, we are still in trouble.

Consider a program with two threads.
One thread processes a list of files, incrementing a counter each time it finishes working on one.
The other thread handles the user interface, periodically reading the counter to update a progress bar.
If that counter is a 64-bit integer, we can not access it atomically on 32-bit machines,
since we need two loads or stores to read or write the entire value.
If we are particularly unlucky, the first thread could be halfway through writing the counter when the second thread reads it,
receiving garbage.
These unfortunate occasions are called *torn reads and writes*.

If reads and writes to the counter are atomic, however, our problem disappears.
We can see that, compared to the difficulties of establishing the right order,
atomicity is fairly straightforward:
just make sure that any variables used for thread synchronization
are no larger than the <small>CPU</small> word size.

<a id="fig:atomicity"></a>
{{#include ../images/atomicity.svg}}
> *A flowchart depicting how two concurrent programs communicate and coordinate through a shared resource to achieve a goal, accessing the shared resource.*

Summary of concepts from the first three sections, as shown in [the figure](#fig:atomicity).
In [Background](./background.html), we observe the importance of maintaining the correct order of operations: \\(t3 \to t4 \to t5 \to t6 \to t7\\), so that two concurrent programs can function as expected.
In [Enforcing law and order](./enforcing_law_and_order.html), we see how two concurrent programs communicate to guarantee the order of operations: \\(t5 \to t6\\).
In *Atomicity*, we understand that certain operations must be treated as a single atomic step to ensure the order of operations: \\(t3 \to t4 \to t5\\) and the order of operations: \\(t6 \to t7\\).
