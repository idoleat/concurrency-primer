# Memory consistency models

Modern concurrent programs execute atop at least two layers that freely reorder memory operations:
optimizing compilers transform the source program, and modern microprocessors retire loads and stores through pipelines, caches, speculation, and store buffers.
The program therefore does not have to run in the exact order in which it was written.
Instead, the system is allowed to change the sequence of operations so long as the observable result remains within an agreed set of valid outcomes.
This agreement between the programmer, the compiler, and the hardware is called a memory consistency model.

Memory consistency models operate at several levels.
For example, a compiler may rearrange instructions while lowering C++ source into assembly, and the processor may further reorder the resulting machine instructions while they execute.
The exact implementation details differ from one layer to another, but each layer must still preserve the outcomes promised by its memory model.

## Sequential consistency (SC)

In the 1970s, Leslie Lamport proposed the most widely cited memory consistency model, sequential consistency (SC), defined as follows:

> A multiprocessor system is sequentially consistent if the result of any execution is the same as if the operations of all the processors were executed in some sequential order, and the operations of each individual processor appear in this sequence in the order specified by its program.

Sequential consistency is easy to reason about because every execution appears to be some interleaving of each thread's program order.
That simplicity comes at a cost: modern hardware and optimizing compilers must give up profitable reorderings in order to preserve the illusion.

A memory consistency model is a semantic contract, not a prescribed implementation.
The machine may execute instructions in a very different order from the source text, provided the final result still matches one of the outcomes allowed by the model.
Sequential consistency therefore does not imply a single execution order or a single result.
It only requires that the execution appear equivalent to some legal interleaving of the participating threads.

To make that concrete, consider the following message-passing litmus test.
Two threads write to and read from two shared variables `x` and `y`, both initially set to `0`.

```c
// Litmus Test: Message Passing
int x = 0;
int y = 0;

// Thread 1        // Thread 2
x = 1;             r1 = y;
y = 1;             r2 = x;
```

If this program is sequentially consistent, then in the global interleaving Thread 1's operations must appear with `x = 1` before `y = 1`, and Thread 2's with `r1 = y` before `r2 = x`.
Across the whole program, the following six interleavings are possible:

:::horizontal

```text
x = 1
y = 1
        r1 = y(1)
        r2 = x(1)
```

```text
x = 1
        r1 = y(0)
y = 1
        r2 = x(1)
```

```text
x = 1
        r1 = y(0)
        r2 = x(1)
y = 1
```

:::

:::horizontal

```text
        r1 = y(0)
x = 1
y = 1
        r2 = x(1)
```

```text
        r1 = y(0)
x = 1
        r2 = x(1)
y = 1
```

```text
        r1 = y(0)
        r2 = x(0)
x = 1
y = 1
```

:::

> *Six possible executions of the message-passing litmus test under sequential consistency.*

None of these executions produce `r1 = 1` and `r2 = 0`.
Sequential consistency therefore allows only `(r1, r2)` to be `(1, 1)`, `(0, 1)`, or `(0, 0)`.
Software may rely on `(1, 0)` never occurring, while hardware remains free to optimize as long as it preserves that guarantee.

<a id="hw-seq-cst"></a>
<!-- IMAGE PLACEHOLDER: images/hw-seq-cst -->

> *A simple model of sequentially consistent hardware.*

[The figure above](#hw-seq-cst) sketches one intuitive implementation: each thread accesses a single shared memory, and that memory processes one read or write at a time.
Real machines are more complicated than that.
They may include private caches, queues, and multiple banks, but they still qualify as sequentially consistent if the externally visible behavior matches the same abstract model.

## Total store order (TSO)

Although sequential consistency is often treated as the gold standard for reasoning about multi-threaded programs, it leaves limited room for performance optimization.
Modern processors therefore tend to implement weaker models.
For example, x86 processors are usually described using the total store order (TSO) model, which can be approximated by the following picture:

<a id="hw-tso"></a>
<!-- IMAGE PLACEHOLDER: images/hw-tso -->

> *A simplified model of x86-TSO hardware.*

Under TSO, all processors can read from a single shared memory, but each processor first places its own writes into a per-core write queue, often called a store buffer.

Consider the following write-queue litmus test:

```c
// Litmus Test: Write Queue (Store Buffer)
int x = 0;
int y = 0;

// Thread 1        // Thread 2
x = 1;             y = 1;
r1 = y;            r2 = x;
```

Sequential consistency does not allow `r1 = r2 = 0`, but TSO does.
Under SC, at least one of `x = 1` or `y = 1` must become visible before the reads occur.
Under TSO, however, both writes may still be sitting in their respective store buffers when the reads execute, so each thread can still observe `0`.

Non-sequentially consistent hardware typically provides memory barriers, or fences, to restore stronger ordering when needed.
On a TSO machine, placing a barrier between the write and the read forces older writes to drain before later reads execute:

```c
// Thread 1           // Thread 2
x = 1;                y = 1;
barrier;              barrier;
r1 = y;               r2 = x;
```

The name total store order comes from the fact that once a write leaves the store buffer and reaches shared memory, every processor agrees on where that write sits relative to other writes.
Different processors may see a write late, but they do not disagree about the final order in which committed writes become visible.

Consider the following Independent Reads of Independent Writes (IRIW) litmus test:

```c
// Litmus Test: Independent Reads of Independent Writes (IRIW)
int x = 0;
int y = 0;

// Thread 1    // Thread 2    // Thread 3    // Thread 4
x = 1;         y = 1;         r1 = x;        r3 = y;
                              r2 = y;        r4 = x;
```

If Thread 3 observes `r1 = 1` and `r2 = 0`, then in the single global store order `x = 1` must have committed before `y = 1`.
If Thread 4 also observes `r3 = 1`, that same global order forces `r4` to see `x = 1` as well, so `r4` can only be `1`.
Under TSO, all threads agree on the order in which committed writes become visible, which rules out the disagreement that IRIW would require.

## Relaxed memory models

<a id="hw-relaxed"></a>
<!-- IMAGE PLACEHOLDER: images/hw-relaxed -->

> *A simplified relaxed model resembling <small>ARM</small> hardware.*

[The figure above](#hw-relaxed) sketches a more relaxed model similar to that used by modern <small>ARM</small> processors.
Each core can read and write through its own local structures, and writes may propagate to other cores in different orders.
Reads may also be delayed or speculated until their values are needed.
This gives the hardware substantially more freedom than either SC or TSO.

One property still remains essential: accesses to the same memory location must obey coherence.
All threads must eventually agree on the order in which writes to a single address become visible.
Without coherence, even simple shared-state programs would be almost impossible to reason about.

The following coherence litmus test is therefore disallowed not only on <small>ARM</small>, but also on x86-TSO and under sequential consistency:

```c
// Litmus Test: Coherence
int x = 0;

// Thread 1    // Thread 2    // Thread 3    // Thread 4
x = 1;         x = 2;         r1 = x;        r3 = x;
                              r2 = x;        r4 = x;
```

No execution may produce `r1 = 1`, `r2 = 2`, `r3 = 2`, and `r4 = 1`, because that would require different threads to disagree about the order of writes to `x`.

Litmus tests like these are commonly checked with tools rather than by hand.
The [`diy`](https://diy.inria.fr/) and [`herd7`](https://github.com/herd/herdtools7) tools let you describe a small concurrent program, choose an architecture or language memory model, and enumerate the outcomes that are allowed.
That workflow is especially useful when validating whether a surprising execution is genuinely permitted by <small>ARM</small>, x86-TSO, or the C++ memory model.
