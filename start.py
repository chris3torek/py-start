"""start.py"""

import errno, os, signal, sys, traceback

def start(func, interrupt_trace=None, exc_trace=None):
    """
    Invoke a program, catch various exits, and catch broken-pipe.

    If interrupt_trace is True, a KeyboardInterrupt will show a
    stack trace.  If False, KeyboardInterrupt will not.  If None
    (the default), KeyboardInterrupt will be set from environment
    PYTHON_DEBUG (anything Python-ly true, i.e., any non-empty
    string, will evaluate as True).

    If exc_trace is True, any other exception will show a stack
    trace.  If False, the stack trace will be omitted.  If None
    (the default), it is set from PYTHON_DEBUG, the same as ^C.
    """

    if interrupt_trace is None:
        interrupt_trace = os.environ.get('PYTHON_DEBUG', False)
    if exc_trace is None:
        exc_trace = os.environ.get('PYTHON_DEBUG', False)

    ret, err1, err2, pipe1, pipe2 = 0, None, None, None, None
    try:
        ret = func()
    except KeyboardInterrupt:
        ret = '\nInterrupted'
        err1 = sys.exc_info()
    except SystemExit as err:
        ret = err.code
    except IOError as err:
        # check for "broken pipe" error
        if err.errno == errno.EPIPE:
            pipe1 = sys.exc_info()
        else:
            err1 = sys.exc_info()
    except:
        err1 = sys.exc_info()
    finally:
        # If we have a broken-pipe situation, this may also raise IOError
        try:
            sys.stdout.flush()
        except IOError as err:
            if err.errno == errno.EPIPE:
                pipe2 = sys.exc_info()
            else:
                err2 = sys.exc_info()
    for prefix, err in (
        (None, err1),
        ('Broken pipe occurred; traceback gives point of detection:\n', pipe1),
        ('I/O error detected during final stdout flush:\n', err2),
        ('Broken pipe detected during final stdout flush\n', pipe2),
    ):
        if err is None:
            continue
        if isinstance(err[0], KeyboardInterrupt):
            flag = intr_trace
        else:
            flag = exc_trace
        if flag:
            if prefix:
                sys.stderr.write(prefix)
            # The tracebacks include __start, which is pointless, so we
            # want to toss it.  Pipe2 has no additional info so toss that
            # entirely.
            if err and err is not pipe2:
                traceback.print_exception(err[0], err[1], err[2].tb_next)
    if pipe1 or pipe2:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGPIPE)
        # should not get here, but if we do, this is close, shell-wise
        ret = 128 + signal.SIGPIPE
    sys.exit(ret)
