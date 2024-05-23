# Read-modify-write

Loads and stores are all well and good,
but sometimes we need to read a value, modify it,
and write it back as a single atomic step.
There are a few common *read-modify-write* (<small>RMW</small>) operations.
In C++, they are represented as member functions of `std::atomic<T>`.
In C, they are freestanding functions.
