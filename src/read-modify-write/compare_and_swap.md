# Compare and swap

Finally, we have *compare-and-swap* (<small>CAS</small>),
sometimes called *compare-and-exchange*.
It allows us to conditionally exchange a value *if* its previous value matches the expected one.
In C and C++, as noted in C11 7.17.7.4, <small>CAS</small> resembles the following,
if it were executed atomically:

```c
/* A is an atomic type. C is the non-atomic type corresponding to A */
bool atomic_compare_exchange_strong(A* obj, C* expected, C desired)
{
    if (memcmp(obj, expected, sizeof(*obj)) == 0) {
        memcpy(obj, &desired, sizeof(*obj));
        return true;
    } else {
        memcpy(expected, obj, sizeof(*obj));
        return false;
    }
}
```

The `_strong` suffix may leave you wondering if there is a corresponding "weak" <small>CAS</small>.
Indeed, there is. However, we will delve into that topic later in [Spurious LL/SC failures](../rmw_with_ll-sc/spurious_ll-sc_failures.html).

Because <small>CAS</small> involves an expected value comparison,
it allows <small>CAS</small> operations to extend beyond just <small>RMW</small> functions.
Here's how it works: First, read the shared resource and use this value as the expected value.
Modify the private variable, and then <small>CAS</small>. Compare the current shared variable with the expected shared variable.
If they match, it indicates that Modify is exclusive, and then write by swapping the shared variable with the private variable.
If they don't match, it implies that interference from another thread has occurred.
Subsequently, update the expected value with the current shared value and retry Modify in a loop.
This iterative process allows <small>CAS</small> to serve as a communication mechanism between threads,
ensuring that entire <small>RMW</small> operations on shared resources are performed atomically.
As shown in [the figure](../read-modify-write.html#fig:atomic-types), compared with *Test-and-set* [Test and set](./test_and_set.html),
a thread that employs <small>CAS</small> can directly use the shared resource to check.
It uses atomic <small>CAS</small> to ensure that the Modify step is atomic,
coupled with a while loop to ensure that the entire <small>RMW</small> can behave atomically.

However, atomic <small>RMW</small> operations here are merely a programming tool for programmers to achieve program logic correctness.
Whether they actually execute atomically depends on how the compiler translates them into atomic instructions for a given hardware instruction set.
At the instruction level, *Exchange*, *Fetch-and-Add*, *Test-and-set*, and <small>CAS</small> are different styles of atomic <small>RMW</small> instructions.
An ISA may provide only some of them,
leaving the rest to compilers to synthesize atomic <small>RMW</small> operations.
For example, in IA32/64 and IBM System/360/z architectures,
*Test-and-set* functionality is directly supported by hardware instructions.
x86 has XCHG and XADD for *Exchange* and *Fetch-and-Add*, but implements *Test-and-set* with XCHG.
Arm takes another approach, providing LL/SC (Load Linked/Store Conditional)-style instructions for all the operations,
with <small>CAS</small> added in Armv8/v9-A.
