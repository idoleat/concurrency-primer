# Enforcing law and order

Establishing order in multithreaded programs varies across different <small>CPU</small> architectures.
For years, systems languages like C and C++ lacked built-in concurrency mechanisms,
compelling developers to rely on assembly or compiler-specific extensions.
This gap was bridged in 2011 when the <small>ISO</small> standards for both languages introduced synchronization tools.
Provided these tools are used correctly,
the compiler ensures that neither its optimization processes nor the <small>CPU</small> will perform reorderings that could lead to data races.[^1]

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
int b_v;

void *threadB()
{
    while(!v_ready) { /* wait */ }
    b_v = v;
    /* Do something */
}
```

The C and C++ standard libraries define a series of these types in `<stdatomic.h>` and `<atomic>`,
respectively.
They look and act just like the integer types they mirror (e.g., `bool` → `atomic_bool`,
`int` → `atomic_int`, etc.),
but the compiler ensures that other variables' loads and stores are not reordered around theirs.

Informally, we can think of atomic variables as rendezvous points for threads.
By making `v_ready` atomic,
`v = 42` is now guaranteed to happen before `v_ready = true` in thread *A*,
just as `b_v = v` must happen after reading `v_ready`
in thread *B*.
Formally, atomic types establish a *single total modification order* where,
"\[...\] the result of any execution is the same as if the reads and writes occurred in some order, and the operations of each individual processor appear in this sequence in the order specified by its program."
This model, defined by Leslie Lamport in 1979,
is called *sequential consistency*.

Notice that using atomic variables as an lvalue expression, such as `v_ready = true` and `while(!v_ready)`, is a convenient alternative to explicitly using `atomic_load` or `atomic_store`.[^2]
As stated in C11 6.7.2.4 and 6.7.3, the properties associated with atomic types are meaningful only for expressions that are
lvalues.
Lvalue-to-rvalue conversion (which models a memory read from an atomic location to a CPU register) strips atomicity along with other qualifiers.

[^1]: The ISO C11 standard adopted its concurrency features,
    almost directly, from the C++11 standard.
    Thus, the functionalities discussed should be the same in both languages,
    with some minor syntactical differences favoring C++ for clarity.

[^2]: Atomic load/store operations are not necessarily generated as atomic instructions.
    Under a weaker consistency model, they could simply be normal load/store operations,
    and their code generation can vary across different architectures.
    Check out [LLVM's documentation](https://llvm.org/docs/Atomics.html#atomics-and-codegen) as an example to see how it is handled.
