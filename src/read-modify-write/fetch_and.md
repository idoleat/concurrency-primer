# Fetch and ...

We can also read a value,
perform a simple operation on it (such as addition, subtraction,
or bitwise <small>AND</small>, <small>OR</small>, <small>XOR</small>) and return its previous value,
all as part of a single atomic operation.
You might recall from the exchange example that additions by the worker thread must be atomic to prevent races, where:

1. The worker thread loads the current counter value and adds one.
2. Before that thread can store the value back,
   the <small>UI</small> thread zeroes the counter.
3. The worker now performs its store, as if the counter was never cleared.
