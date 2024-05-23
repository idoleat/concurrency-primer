# Background

Modern computers execute multiple instruction streams concurrently.
On single-core systems, these streams alternate, sharing the <small>CPU</small> in brief time slices.
Multi-core systems, however, allow several streams to run in parallel.
These streams are known by various names such as processes, threads, tasks,
interrupt service routines (ISR), among others, yet many of the same principles govern them all.

Despite the development of numerous sophisticated abstractions by computer scientists,
these instruction streams—hereafter referred to as "*threads*" for simplicity—primarily interact through shared state.
Proper functioning hinges on understanding the sequence in which threads read from and write to memory.
Consider a simple scenario where thread *A* communicates an integer with other threads:
it writes the integer to a variable and then sets a flag, signaling other threads to read the newly stored value.
This operation could be conceptualized in code as follows:

```c
int v;
bool v_ready = false;

void threadA()
{
    // Write the value
    // and set its ready flag.
    v = 42;
    v_ready = true;
}
```
```c
void threadB()
{
    // Await a value change and read it.
    while (!v_ready) { /* wait */ }
    const int my_v = v;
    // Do something with my_v...
}
```

We must ensure that other threads only observe *A*'s write to `v_ready` *after A's* write to `v`.
If another thread can "see" `v_ready` becoming true before observing `v` becoming \\(42\\),
this simple scheme will not work correctly.

One might assume it is straightforward to ensure this order,
yet the reality is often more complex.
Initially, any optimizing compiler will restructure your code to enhance performance on its target hardware.
The primary objective is to maintain the operational effect within *the current thread*,
allowing reads and writes to be rearranged to prevent pipeline stalls[^a] or to optimize data locality.[^b]

Variables may be allocated to the same memory location if their usage does not overlap.
Furthermore, calculations might be performed speculatively ahead of a branch decision and subsequently discarded if the branch prediction proves incorrect.[^c]
<!--These sorts of optimizations  sometimes called the ``as-if'' rule in \cplusplus{}.-->

Even without compiler alterations,
we would face challenges because our hardware complicates matters further!
Modern <small>CPU</small>s operate in a fashion far more complex than what traditional pipelined methods,
like those depicted in \fig{pipeline}<!--FIXME-->, suggest.
They are equipped with multiple data paths tailored for various instruction types and schedulers that reorder and direct instructions through these paths.

{{#include images/pipeline.svg}}
*<figcaption>A traditional five-stage <small>CPU</small> pipeline with fetch, decode, execute, memory access, and write-back stages. Modern designs are much more complicated, often reordering instructions on the fly.</figcaption>*

It is quite common to form oversimplified views about memory operations.
Picturing a multi-core processor setup might lead us to envision a model similar to \fig{ideal-machine}, <!--FIXME-->
wherein each core alternately accesses and manipulates the system's memory.

{{#include images/ideal-machine.svg}}
*<figcaption>An idealized multi-core processor where cores take turns accessing a single shared set of memory.</figcaption>*

The reality is far from straightforward.
Although processor speeds have surged exponentially in recent decades,
<small>RAM</small> has struggled to match pace,
leading to a significant gap between the execution time of an instruction and the time required to fetch its data from memory.
To mitigate this, hardware designers have incorporated increasingly complex hierarchical caches directly onto the <small>CPU</small> die.
Additionally, each core often features a *store buffer* to manage pending writes while allowing further instructions to proceed.
Ensuring this memory system remains *coherent*,
thus allowing writes made by one core to be observable by others even when utilizing different caches,
presents a significant challenge.

{{#include images/mp-cache.svg}}
*<figcaption>A common memory hierarchy for modern multi-core processors.</figcaption>*

The myriad complexities within multithreaded programs on multi-core <small>CPU</small>s lead to a lack of a uniform concept of "now".
Establishing some semblance of order among threads requires a concerted effort involving the hardware,
compiler, programming language, and your application.
Let's delve into our options and the tools necessary for this endeavor.

[^a]: Most <small>CPU</small> architectures execute segments of multiple instructions concurrently to improve throughput (refer to \fig{pipeline}).<!--FIXME-->
A stall, or suspension of forward progress, occurs when an instruction awaits the outcome of a preceding one in the pipeline until the necessary result becomes available.

[^b]: <small>RAM</small> accesses data not byte by byte, but in larger units known as *cache lines*.
Grouping frequently used variables on the same cache line means they are processed together,
significantly boosting performance. However, as discussed in \secref{false-sharing}, <!--FIXME-->
this strategy can lead to complications when cache lines are shared across cores.

[^c]: Profile-guided optimization (PGO) often employs this strategy.
