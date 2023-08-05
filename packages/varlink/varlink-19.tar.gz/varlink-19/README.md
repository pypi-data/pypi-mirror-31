[![Build Status](https://travis-ci.org/varlink/python.svg?branch=master)](https://travis-ci.org/varlink/python)
[![Coverage Status](https://coveralls.io/repos/github/varlink/python/badge.svg?branch=master)](https://coveralls.io/github/varlink/python?branch=master)

# python-varlink

A [varlink](http://varlink.org) implementation for Python.

## varlink tool installation

With Fedora 28/rawhide:
```bash
$ sudo dnf install python-varlink libvarlink-util
```

## Examples

See the [tests](https://github.com/varlink/python-varlink/tree/master/varlink/tests) directory.

```bash
$ PYTHONPATH=$(pwd) python3 ./varlink/tests/test_orgexamplemore.py --varlink="unix:@test" &
[1] 6434
$ varlink help unix:@test/org.example.more
# Example Varlink service
interface org.example.more

# Enum, returning either start, progress or end
# progress: [0-100]
type State (
  start: ?bool,
  progress: ?int,
  end: ?bool
)

# Returns the same string
method Ping(ping: string) -> (pong: string)

# Dummy progress method
# n: number of progress steps
method TestMore(n: int) -> (state: State)

# Stop serving
method StopServing() -> ()

# Something failed in TestMore
error TestMoreError (reason: string)


$ fg
PYTHONPATH=$(pwd) python3 ./varlink/tests/test_orgexamplemore.py --varlink="unix:@test"
^C
```

```bash
$ PYTHONPATH=$(pwd) python3 ./varlink/tests/test_orgexamplemore.py
Connecting to exec:./varlink/tests/test_orgexamplemore.py

Listening on @0002c
Ping:  Test
--- Start ---
Progress: 0
Progress: 10
Progress: 20
Progress: 30
Progress: 40
Progress: 50
Progress: 60
Ping:  Test
Progress: 70
Ping:  Test
Progress: 80
Ping:  Test
Progress: 90
Ping:  Test
Progress: 100
Ping:  Test
--- End ---
```

```bash
$ PYTHONPATH=$(pwd) python3 ./varlink/tests/test_orgexamplemore.py --varlink="unix:@test" &
Listening on @test
[1] 6434
$ PYTHONPATH=$(pwd) python3 ./varlink/tests/test_orgexamplemore.py --client --varlink="unix:@test"
Connecting to unix:@test

Ping:  Test
--- Start ---
Progress: 0
Progress: 10
Progress: 20
Progress: 30
Progress: 40
Progress: 50
Progress: 60
Ping:  Test
Progress: 70
Ping:  Test
Progress: 80
Ping:  Test
Progress: 90
Ping:  Test
Progress: 100
Ping:  Test
--- End ---
$ fg
PYTHONPATH=$(pwd) python3 ./varlink/tests/test_orgexamplemore.py --varlink="unix:@test"
^C
```

You can also start the clients and server with URLs following the [varlink URL standard](https://github.com/varlink/documentation/wiki#address).
E.g.
- unix:@anonuds
- unix:/run/myserver/socketfile
- tcp:127.0.0.1:12345
- tcp:[::1]:12345
