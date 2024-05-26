# Acquire and release

We have just examined the acquire and release operations in the context of the lock example from [last chapter](/do_we_always_need_seq-cst.html).
You can think of them as "one-way" barriers: an acquire operation permits other reads and writes to move past it,
but only in a \\(before\to after\\) direction.
A release works the opposite manner, allowing actions to move in an \\(after\to before\\) direction.
On <small>Arm</small> and other weakly-ordered architectures, this enables us to eliminate one of the memory barriers in each operation,
such that

:::horizontal
```cpp
int acquireFoo()
{
    return foo.load(memory_order_acquire);
}
```
\\[
\text{ } \xrightarrow{\textit{becomes}} \text{ }
\\]
```armasm
acquireFoo:
  ldr r3, <&foo>
  ldr r0, [r3, #0]
  dmb
  bx lr
```
:::

:::horizontal
```cpp
void releaseFoo(int i)
{
    foo.store(i, memory_order_release);
}
```
\\[
\text{ } \xrightarrow{\textit{becomes}} \text{ }
\\]
```armasm
releaseFoo:
  ldr r3, <&foo>
  dmb
  str r0, [r3, #0]
  bx lr
```
:::

Together, these provide \\(writer\to reader\\) synchronization:
if thread *W* stores a value with release semantics,
and thread *R* loads that value with acquire semantics,
then all writes made by *W* before its store-release are observable to *R* after its load-acquire.
If this sounds familiar, it is exactly what we were trying to achieve in
chapter [background](/background.html) and [enforcing law and order](/enforcing_law_and_order.html):
```cpp
int v;
std::atomic_bool v_ready(false);

void threadA()
{
    v = 42;
    v_ready.store(true, memory_order_release);
}

void threadB()
{
    while (!v_ready.load(memory_order_acquire)) {
        // wait
    }
    assert(v == 42); // Must be true
}
```
