# Exchange

The simplest atomic <small>RMW</small> operation is an *exchange*:
the current value is read and replaced with a new one.
To see where this might be useful,
let's tweak our example from chapter [Atomicity](/atomicity.html):
instead of displaying the total number of processed files,
the <small>UI</small> might want to show how many were processed per second.
We could implement this by having the <small>UI</small> thread read the counter then zero it each second.
But we could get the following race condition if reading and zeroing are separate steps:

1. The <small>UI</small> thread reads the counter.
2. Before the <small>UI</small> thread has the chance to zero it,
   the worker thread increments it again.
3. The <small>UI</small> thread now zeroes the counter, and the previous increment is lost.

If the <small>UI</small> thread atomically exchanges the current value with zero,
the race disappears.
