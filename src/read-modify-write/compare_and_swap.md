# Compare and swap

Finally, we have *compare-and-swap* (<small>CAS</small>),
sometimes called *compare-and-exchange*.
It allows us to conditionally exchange a value *if* its previous value matches some expected one.
In C and C++, <small>CAS</small> resembles the following,
if it were executed atomically:

```cpp
template <typename T>
bool atomic<T>::compare_exchange_strong(
    T& expected, T desired)
{
    if (*this == expected) {
        *this = desired;
        return true;
    }
    expected = *this;
    return false;
}

```

The `compare_exchange_strong` suffix may leave you wondering if there is a corresponding "weak" <small>CAS</small>.
Indeed, there is. However, we will delve into that topic later in chapter [Spurious LL/SC failures](../spurious_ll-sc_failures.html).
Let's say we have some long-running task that we might want to cancel.
We'll give it three states: *idle*, *running*, and *cancelled*, and write a loop that exits when it is cancelled.

```c++
enum class TaskState : int8_t {
    Idle, Running, Cancelled
};

std::atomic<TaskState> ts;

void taskLoop()
{
    ts = TaskState::Running;
    while (ts == TaskState::Running) {
      // Do good work.
    }
}
```

If we want to cancel the task if it is running, but do nothing if it is idle,
we could <small>CAS</small>:

```c++
bool cancel()
{
    auto expected = TaskState::Running;
    return ts.compare_exchange_strong(expected, TaskState::Cancelled);
}
```
