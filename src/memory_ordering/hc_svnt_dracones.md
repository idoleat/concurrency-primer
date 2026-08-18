# <small>HC SVNT DRACONES</small>

Non-sequentially consistent orderings have many subtleties,
and a slight mistake can cause elusive Heisenbugs that only happen sometimes,
on some platforms.
Before reaching for them, ask yourself:

-   Am I using a well-known and understood pattern\
    (such as the ones shown above)?

-   Are the operations in a tight loop?

-   Does every microsecond count here?

If the answer is not yes to several of these,
stick to sequentially consistent operations.
Otherwise, be sure to give your code extra review and testing.
