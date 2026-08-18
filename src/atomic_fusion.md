# Atomic fusion

Finally, one should realize that while atomic operations do prevent certain optimizations,
they are not somehow immune to all of them.
The optimizer can do fairly mundane things, such as replacing
`foo.fetch_and(0)` with `foo = 0`,
but it can also produce surprising results.
Consider:

```cpp
while (tmp = foo.load(memory_order_relaxed)) {
    doSomething(tmp);
}
```

Since relaxed loads provide no ordering guarantees,
the compiler is free to unroll the loop as much as it pleases,
perhaps into:

```cpp
while (tmp = foo.load(memory_order_relaxed)) {
    doSomething(tmp);
    doSomething(tmp);
    doSomething(tmp);
    doSomething(tmp);
}
```

If "fusing" reads or writes like this is unacceptable,
we must prevent it
with `volatile` casts or incantations like `asm volatile("" ::: "memory")`.[^1]
The Linux kernel provides `READ_ONCE()` and `WRITE_ONCE()`
macros for this exact purpose.[^2]

[^1]: See
    <https://stackoverflow.com/a/14983432>.

[^2]: See
    [<small>N</small>4374](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4374.html)
    and the kernel's
    [`rwonce.h`](https://elixir.bootlin.com/linux/latest/source/include/asm-generic/rwonce.h) for details.
