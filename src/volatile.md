# If concurrency is the question, `volatile` is not the answer.

Before we go, we should lay a common misconception surrounding the `volatile` keyword to rest.
Perhaps because of how it worked in older compilers and hardware,
or due to its different meaning in languages like Java and C#,\punckern<small>footnote</small>[^a]
some believe that the keyword is useful for building concurrency tools.
Except for one specific case (see \secref{fusing}<!--FIXME-->), this is false.

The purpose of `volatile` is to inform the compiler that a value can be changed by something besides the program we are executing.
This is useful for memory-mapped <small>IO</small> (<small>MMIO</small>),
where hardware translates reads and writes to certain addresses into instructions for the devices connected to the <small>CPU</small>.
(This is how most machines ultimately interact with the outside world.)
`volatile` implies two guarantees:
1. The compiler will not elide loads and stores that seem "unnecessary". For example, if I have some function:
    ```cpp
    void write(int *t)
    {
        *t = 2;
        *t = 42;
    }
    ```
    the compiler would normally optimize it to:
    ```cpp
    void write(int *t)
    {
        *t = 42;
    }
    ```
    `*t = 2` is often considered a *dead store*,
    seemingly performing no function.
    However, when `t` is directed at an <small>MMIO</small> register,
    this assumption becomes unsafe.
    In such cases, each write operation could potentially influence the behavior of the associated hardware.
2. The compiler will not reorder `volatile` reads and writes with respect to other `volatile` ones for similar reasons.

These rules fall short of providing the atomicity and order required for safe communication between threads.
It is important to note that the second rule only prevents `volatile` operations from being reordered in relation to one another.
The compiler remains at liberty to reorganize all other "normal" loads and stores around them.
Furthermore, even setting this issue aside,
`volatile` does not generate memory barriers on hardware with weak ordering.
The effectiveness of the keyword as a synchronization tool hinges on both the compiler and the hardware avoiding any reordering,
which is not a reliable expectation.

[^a]: Unlike in C and C++,
`volatile` *does* enforce ordering in those languages.
