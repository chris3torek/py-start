"""start.py"""

import errno, os, signal, sys, traceback

def start(func, interrupt_trace=None, exc_trace=None):
    """
    Invoke a program, catch various exits, and catch broken-pipe.

    If interrupt_trace is True, a KeyboardInterrupt will show a
    stack trace.  If False, KeyboardInterrupt will not.  If None
    (the default), KeyboardInterrupt will be set from environment
    PYTHON_DEBUG (anything Pythonically true, i.e., any non-empty
    string, will evaluate as True).

    If exc_trace is True, any other exception will show a stack
    trace.  If False, the stack trace will be omitted.  If None
    (the default), it is set from PYTHON_DEBUG, the same as ^C.
    """

    is_intr = lambda err: isinstance(err[1], KeyboardInterrupt)
    is_err_and_intr = lambda err: err is not None and is_intr(err)

    if interrupt_trace is None:
        interrupt_trace = os.environ.get('PYTHON_DEBUG', False)
    if exc_trace is None:
        exc_trace = os.environ.get('PYTHON_DEBUG', False)

    ret, err1, err2, pipe1, pipe2 = 0, None, None, None, None
    try:
        ret = func()
    except KeyboardInterrupt:
        ret = 1
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
    if interrupt_trace or exc_trace:
        for prefix, err in (
            (None, err1),
            ('Broken pipe -- traceback gives point of detection:\n', pipe1),
            ('I/O error detected during final stdout flush:\n', err2),
            ('Broken pipe detected during final stdout flush\n', pipe2),
        ):
            if err is None:
                continue
            flag = interrupt_trace if is_intr(err) else exc_trace
            if flag:
                if prefix:
                    sys.stderr.write(prefix)
                # The tracebacks include us, which is pointless, so we
                # want to toss one frame.  Pipe2 has no additional info
                # so toss that entirely.
                if err and err is not pipe2:
                    traceback.print_exception(err[0], err[1], err[2].tb_next)

    # Translate interrupt and pipe back to signal-exit, if we're
    # behaving like a typical Unix utility.
    if not interrupt_trace and (is_err_and_intr(err1) or is_err_and_intr(err2)):
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            os.kill(os.getpid(), signal.SIGINT)
            ret = 128 + signal.SIGINT
    if pipe1 or pipe2:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGPIPE)
        # should not get here, but if we do, this is close, shell-wise
        ret = 128 + signal.SIGPIPE
    sys.exit(ret)
