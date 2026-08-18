# Lock-free

In [Concurrency tools and synchronization mechanisms](./concurrency_tools.html), we explored different mechanisms based on the characteristics of concurrency tools,
as described in [Atomicity](./atomicity.html) and [Read-modify-write](./read-modify-write.html).
In this section, we need to explore which strategies can help programmers to design a concurrency program
that allows concurrent threads to collectively ensure progress in the overall system while also improving scalability,
which is the initial goal of designing a concurrency program.
First of all, we must figure out the scope of our problem.
Understanding the relationship between the progress of each thread and the progress of the entire system is necessary.
