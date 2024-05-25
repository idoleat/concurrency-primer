# Sequential consistency on weakly-ordered hardware

Different hardware architectures offer distinct memory models or *memory models*.
For instance, x64 architecture[^a] is known to be *strongly-ordered*,
generally ensuring a global sequence for loads and stores in most scenarios.
Conversely, architectures like <small>Arm</small> are considered *weakly-ordered*,
meaning one should not expect loads and stores to follow the program sequence without explicit instructions to the <small>CPU</small>.
These instructions, known as *memory barriers*, are essential to prevent the reordering of these operations.

It is helpful to see how atomic operations work in a weakly-ordered system,
both to understand what's happening in hardware,
and to see why the C and C++ concurrency models were designed as they were.[^b]
Let's examine <small>Arm</small>, since it is both popular and straightforward.
Consider the simplest atomic operations: loads and stores.
Given some `atomic_int foo`,

:::horizontal
```c
int getFoo()
{
    return foo;
}
```
\\[
\text{ } \xrightarrow{\textit{becomes}} \text{ }
\\]
```armasm
getFoo:
  ldr r3, <&foo>
  dmb
  ldr r0, [r3, #0]
  dmb
  bx lr
```
:::

:::horizontal
```c
void setFoo(int i)
{
    foo = i;
}
```
\\[
\text{ } \xrightarrow{\textit{becomes}} \text{ }
\\]
```armasm
setFoo:
  ldr r3, <&foo>
  dmb
  str r0, [r3, #0]
  dmb
  bx lr
```
:::

We load the address of our atomic variable into a scratch register `r3`,
place our load or store operation between memory barriers `dmb`, and then proceed.
These barriers ensure sequential consistency:
the first barrier guarantees that previous reads and writes are not reordered to follow our operation,
and the second ensures that future reads and writes are not reordered to precede it.

[^a]: Also known as x86-64, x64 is a 64-bit extension of the x86 instruction set, officially unveiled in 1999.
This extension heralded the introduction of two novel operation modes:
64-bit mode for leveraging the full potential of 64-bit processing and compatibility mode for maintaining support for 32-bit applications.
Initially developed by AMD and publicly released in 2000, the x64 architecture has since been adopted by Intel and VIA,
signaling a unified industry shift towards 64-bit computing.
This wide adoption marked the effective obsolescence of the Intel Itanium architecture (IA-64),
despite its initial design to supersede the x86 architecture.

[^b]: It is worth noting that the concepts we discuss here are not specific to C and C++.
Other systems programming languages like D and Rust have converged on similar models.
