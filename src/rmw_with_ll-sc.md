# Implementing atomic read-modify-write operations with LL/SC instructions

Like many <small>RISC</small>[^a] architectures,
<small>Arm</small> does not have dedicated <small>RMW</small> instructions.
Given that the processor may switch contexts to another thread at any moment,
constructing <small>RMW</small> operations from standard loads and stores is not feasible.
Special instructions are required instead: *load-link* and *store-conditional* (<small>LL/SC</small>).
These instructions are complementary:
load-link performs a read operation from an address, similar to any load,
but it also signals the processor to watch that address.
Store-conditional executes a write operation only if no other writes have occurred at that address since its paired load-link.
This mechanism is illustrated through an atomic fetch and add example.

On <small>Arm</small>
```c
void incFoo() { ++foo; }
```
compiles to
```armasm
incFoo:
  ldr r3, <&foo>
  dmb
loop:
  ldrex r2, [r3] // LL foo
  adds r2, r2, #1 // Increment
  strex r1, r2, [r3] // SC
  cmp r1, #0 // Check the SC result.
  bne loop // Loop if the SC failed.
  dmb
  bx lr
```
We <small>LL</small> the current value, add one, and immediately try to store it back with a <small>SC</small>.
If that fails, another thread may have written to `foo` since our <small>LL</small>, so we try again.
In this way, at least one thread is always making forward progress in atomically modifying `foo`,
even if several are attempting to do so at once.


[^a]: *Reduced instruction set computer*, in contrast to a *complex instruction set computer* (<small>CISC</small>) architecture like x64.
