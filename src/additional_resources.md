# Additional Resources

[C++ atomics, from basic to advanced. What do they really do?](https://www.youtube.com/watch?v=ZQFzMfHIxng)
by Fedor Pikus,
a hour-long talk on this topic.

[C++ atomic<> Weapons: The C++11 Memory Model and Modern Hardware](https://herbsutter.com/2013/02/11/atomic-weapons-the-c-memory-model-and-modern-hardware/)
by Herb Sutter,
a three-hour talk that provides a deeper dive.
Also the source of figures \ref{ideal-machine} and \ref{dunnington}.<!--FIXME-->

[Futexes are Tricky](https://www.akkadia.org/drepper/futex.pdf),
a paper by Ulrich Drepper on how mutexes and other synchronization primitives can be built in Linux using atomic operations and syscalls.

[Is Parallel Programming Hard, And, If So, What Can You Do About It?](https://www.kernel.org/pub/linux/kernel/people/paulmck/perfbook/perfbook.html),
by Paul E. McKenney,
an *incredibly* comprehensive book covering parallel data structures and
algorithms, transactional memory, cache coherence protocols,
<small>CPU</small> architecture specifics, and more.

[Memory Barriers: a Hardware View for Software Hackers](http://www.rdrop.com/~paulmck/scalability/paper/whymb.2010.06.07c.pdf),
an older but much shorter piece by McKenney explaining how memory barriers are implemented
in the Linux kernel on various architectures.

[Preshing On Programming](https://preshing.com/archives/),
a blog with many excellent articles on lockless concurrency.

*No Sane Compiler Would Optimize Atomics*,
a discussion of how atomic operations are handled by current optimizers.
Available as a writeup,
[<small>N</small>4455](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4455.html), and as a
[CppCon talk](https://www.youtube.com/watch?v=IB57wIf9W1k).

[cppreference.com](https://en.cppreference.com),
an excellent reference for the C and C++ memory model and atomic <small>API</small>.

[Matt Godbolt's Compiler Explorer](https://godbolt.org/),
an online tool that provides live, color-coded disassembly using compilers and flags of your choosing.
*Fantastic* for examining what compilers emit for various atomic operations on different architectures.
