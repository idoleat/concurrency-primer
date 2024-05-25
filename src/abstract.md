# Concurrency Primer <small><small><small>[^note]</small></small></small>
Matt Kline and Ching-Chun (Jim) Huang  

## Abstract
System programmers are acquainted with tools such as mutexes, semaphores, and condition variables.
However, the question remains: how do these tools work, and how do we write concurrent code in their absence?
For example, when working in an embedded environment beneath the operating system,
or when faced with hard time constraints that prohibit blocking.
Furthermore, since the compiler and hardware often combine to transform code into an unanticipated order,
how do multithreaded programs work? Concurrency is a complex and counterintuitive topic,
but let us endeavor to explore its fundamental principles.

[^note]: The original title was *"What every systems programmer should know about concurrency"*
