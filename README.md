start.py is a wrapper that can be used on Unix-like systems
to turn Python programs into relatively well behaved Unix
utilities.

Specifically, it:

 * catches KeyboardInterrupt and makes the program die of SIGINT
   (without a stack traceback, by default)
 * catches SIGPIPE and makes the program die with a SIGPIPE
   (without a stack traceback, by default)
 * catches other exceptions and writes the traceback to a `.core` file

Core files are appended-to, with a timestamp of the problem, so
that these "core dumps" can be delivered to maintainers.

If you are actively developing your code and want ^C and/or
traps to show you the stack trace in the usual fashion, set
environment variables `PYTHON_SIGINT=true` and/or `PYTHON_DEBUG=true`
(using `export` from sh/bash, or in front of the command being
run, as in `PYTHON_DEBUG=true python myprog.py`.

The code is compatible (and tested) with both Python 2.7 and 3.4.

Currently I think the traceback code may need a bit of work on
Python 3 (because some items may not UTF-8 encode properly and
the current code does not attempt to save them in a reversible
format).
