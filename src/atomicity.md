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
