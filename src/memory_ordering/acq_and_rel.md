# Acquire and release

We have just examined the acquire and release operations in the context of the lock example from \secref{lock-example}.<!--FIXME-->
You can think of them as "one-way" barriers: an acquire operation permits other reads and writes to move past it,
but only in a \\(before\to after\\) direction.
A release works the opposite manner, allowing actions to move in an after→before direction.
On <small>Arm</small> and other weakly-ordered architectures, this enables us to eliminate one of the memory barriers in each operation,
such that

<div class="hori_container">

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
</div>

<div class="hori_container">

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
</div>

Together, these provide \\(writer\to reader\\) synchronization:
if thread *W* stores a value with release semantics,
and thread *R* loads that value with acquire semantics,
then all writes made by *W* before its store-release are observable to *R* after its load-acquire.
If this sounds familiar, it is exactly what we were trying to achieve in
\secref{background} and \secref{seqcst}: <!--FIXME-->
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
