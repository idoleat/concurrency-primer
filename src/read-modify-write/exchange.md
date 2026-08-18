# Exchange

Transform <small>RMW</small> into modifying a private variable first,
and then directly swapping the private variable with the shared variable.
Therefore, we only need to ensure that the second step,
which involves a Read that loads the shared variable, followed by Modify and Write steps that exchange it with the private variable,
is a single atomic step.
This allows programmers to extensively modify the private variable beforehand and only write it to the shared variable when necessary. 
