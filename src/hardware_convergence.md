# Hardware convergence

Those familiar with <small>Arm</small>, may have noticed that all assembly shown here is for the seventh version of the architecture.
Excitingly, the eighth generation offers massive improvements for lockless code.
Since most programming languages have converged on the memory model we have been exploring,
<small>Arm</small>v8 processors offer dedicated load-acquire and store-release instructions: `lda` and `stl`.
Hopefully, future <small>CPU</small> architectures will follow suit.
