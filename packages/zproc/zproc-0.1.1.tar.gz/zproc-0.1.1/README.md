# ZProc - Process on steroids
zproc is short for [Zero](http://zguide.zeromq.org/page:all#The-Zen-of-Zero) - [Process](https://docs.python.org/3.6/library/multiprocessing.html#multiprocessing.Process)

zproc aims to reduce the pain of multi-processing by

- 🌠
    - Sync-ing  application state across all processes (without shared varialbes!).
- 🌠
    - Giving you the freedom to build any combination of synchronous or asynchronous systems.
- 🌠
    - Remembers to kill processes when exiting, for general peace.

# Example
###### `state` is NOT a shared variable!. It's actually a remote object that is wrapped to behave like a dict.


```
from time import sleep

import zproc


def child1(state, props):
    state.get_when_change('foo')
    print("child1: foo got updated, so I wake")

    state['bar'] = 'xxx'
    print('child1: I set bar to xxx')
    print('child1: I exit')


def bar_equals_xxx(state):
    return state.get('bar') == 'xxx'


def child2(state, props):
    state.get_when(bar_equals_xxx)
    print('child2: bar changed to xxx, so I wake')
    print('child2: I exit')


ctx = zproc.Context()

ctx.process_factory(child1, child2, props='hello!')
ctx.start_all()

sleep(1)

ctx.state['foo'] = 'foobar'
print('child0: I set foo to foobar')

input()

print('child0: I exit')
```

###### output
```
child0: I set foo to foobar
child1: foo got updated, so I wake
child1: I set bar to xxx
child1: I exit
child2: bar changed to xxx, so I wake
child2: I exit

child0: I exit
```

# Inner Workings

- The process(s) communicate over zmq sockets, over `ipc://`.

- The parent process has its own Process attached; responsible for the following

    - storing the state whenever it is updated, by another process.

    - transmitting the state whenever a process needs to access it.

- If a process wishes to synchronize at a certain condition, it can attach a handler to the zproc daemon.

    - The zproc daemon will check the condition on all state-changes.

    - If the condition is met, the zproc daemon shall open a tunnel to the application and send the state back.

    - zmq already has the mechanisms to block your application untill that tunnel is opened.

# Caveats

- The state only gets updated if you do it directly. This means that if you mutate objects in the state, they wont get updated in global state.

- It runs an extra daemonic process for managing the state. Its fairly lightweight though, and shouldn't add too much weight to your application.

- The state is required to be marshal compatible, which means:

> The following types are supported: booleans, integers, floating point numbers, complex numbers, strings, bytes, bytearrays, tuples, lists, sets, frozensets, dictionaries, and code objects, where it should be understood that tuples, lists, sets, frozensets and dictionaries are only supported as long as the values contained therein are themselves supported. The singletons None, Ellipsis and StopIteration can also be marshalled and unmarshalled

(from python [docs](https://docs.python.org/3/library/marshal.html))

# Known issues

- Processes inside processes are known to create wierd behavior like
    - not being able to access state
    - not shutting down properly on exit


# Install
`pip install zproc`
