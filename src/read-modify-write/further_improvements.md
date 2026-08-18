# Further improvements

At the beginning of [Read-modify-write](../read-modify-write.html), we described how a global total order is established by combining local order and inter-thread order imposed by atomic objects.
But should every object, including non-atomic ones, participate in a single global order established by atomic objects?
*Sequential consistency* solves the ordering problem in [Enforcing law and order](../enforcing_law_and_order.html), but it may force too much ordering, as some normal operations may not require it.
By default, atomic operations in the C11 atomic library use `memory_order_seq_cst` as the default memory order. Operations with the `_explicit` suffix accept an additional argument to specify which memory order to use.
How to leverage memory orders to optimize performance will be covered later in [Do we always need sequentially consistent operations?](../do_we_always_need_seq-cst.html).
