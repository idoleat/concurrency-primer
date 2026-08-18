# Fetch and...

Transform <small>RMW</small> to directly modify the shared variable (such as addition, subtraction,
or bitwise <small>AND</small>, <small>OR</small>, <small>XOR</small>) and return its previous value,
all as part of a single atomic operation.
Compared with *Exchange* in [Exchange](./exchange.html), when programmers only need to make a simple modification to the shared variable,
they can use *Fetch-and...*.
