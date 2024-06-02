# Enforcing law and order

Establishing order in multithreaded programs varies across different <small>CPU</small> architectures.
For years, systems languages like C and C++ lacked built-in concurrency mechanisms,
compelling developers to rely on assembly or compiler-specific extensions.
This gap was bridged in 2011 when the <small>ISO</small> standards for both languages introduced synchronization tools.
Provided these tools are used correctly,
the compiler ensures that neither its optimization processes nor the <small>CPU</small> will perform reorderings that could lead to data races.[^a]

To ensure our earlier example functions as intended,
the "ready" flag must utilize an *atomic type*.

```c
#include <stdatomic.h>
int v = 0;
atomic_bool v_ready = false;

void *threadA()
{
    v = 42;
    v_ready = true;
}
```
```c
int bv;

void *threadB()
{
    while(!v_ready) { /* wait */ }
    bv = v;
    /* Do something */
}
```

The C and C++ standard libraries define a series of these types in `<stdatomic.h>` and `atomic`,
respectively.
They look and act just like the integer types they mirror (e.g., `bool`\\(\to\\)`atomic_bool`},
`int`\\(\to\\)`atomic_int`, etc.),
but the compiler ensures that other variables' loads and stores are not reordered around theirs.

Informally, we can think of atomic variables as rendezvous points for threads.
By making `v_ready` atomic,
`v = 42`, is now guaranteed to happen before `v_ready = true`, in thread *A*,
just as `my_v = v`, must happen after reading `v_ready`,
in thread *B*.
Formally, atomic types establish *single total modification order* where,
"[...] the result of any execution is the same as if the reads and writes occurred in some order, and the operations of each individual processor appear in this sequence in the order specified by its program."
This model, defined by Leslie Lamport in 1979,
is called \\(sequential\space consistency\\).

[^a]: The ISO C11 standard adopted its concurrency features,
almost directly, from the C++11 standard.
Thus, the functionalities discussed should be the same in both languages,
with some minor syntactical differences favoring C++ for clarity.
