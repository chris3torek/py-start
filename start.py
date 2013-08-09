"""start.py"""

import errno, os, signal, sys, traceback

def sigdie(sig):
    """Attempt to die from a signal.
    """
    signal.signal(sig, signal.SIG_DFL)
    os.kill(os.getpid(), sig)
    # We should not get here, but if we do, this exit() status
    # is as close as we can get to what happens when we die from
    # a signal.
    return 128 + sig

def _split_err(err):
    """Split exc_info() (if any) into one of two "signal based"
    errors, or generic non-signal error.  Returns a trio
    (pipe_err, intr_err, regular_err) with at most one being
    non-None.
    """
    if err is None:
        return None, None, None
    if isinstance(err[1], IOError) and err[1].errno == errno.EPIPE:
        return err, None, None
    if isinstance(err[1], KeyboardInterrupt):
        return None, err, None
    return None, None, err

def _show_err(err, prefix=None):
    """Dump traceback from exc_info() error, but leave out the
    first frame, which is start() itself, and do nothing if err
    is None.
    """
    if err:
        if prefix:
            sys.stderr.write(prefix)
        traceback.print_exception(err[0], err[1], err[2].tb_next)

def start(func, interrupt_trace=None, exc_trace=None):
    """
    Invoke a program, catch various exits, and catch broken-pipe.

    If interrupt_trace is True, a KeyboardInterrupt will show a
    stack trace.  If False, KeyboardInterrupt will not.  If None
    (the default), KeyboardInterrupt will be set from environment
    PYTHON_SIGINT (anything Pythonically true, i.e., any non-empty
    string, will evaluate as True).

    If exc_trace is True, any other exception will show a stack
    trace.  If False, the stack trace will be omitted.  If None
    (the default), it is set from PYTHON_DEBUG; the rest is just
    like KeyboardInterrupt.

    In any case, signals (specifically SIGINT and SIGPIPE) that
    were caught and translated into an exception, are translated
    back to a signal-style exit, so as to make this a well behaved
    Unix utility.
    """

    if interrupt_trace is None:
        interrupt_trace = os.environ.get('PYTHON_SIGINT', False)
    if exc_trace is None:
        exc_trace = os.environ.get('PYTHON_DEBUG', False)

    ret, err1, err2 = None, None, None

    try:
        ret = func()
    except SystemExit as err:
        ret = err.code
    except:
        err1 = sys.exc_info()
    finally:
        # This may also cause broken pipe or get interrupted (or
        # do all kinds of things if sys.stdout has been wrapped).
        try:
            sys.stdout.flush()
        except SystemExit as err:
            ret = err.code # should we keep any earlier SystemExit val?
        except:
            err2 = sys.exc_info()

    pipe1, intr1, err1 = _split_err(err1)
    pipe2, intr2, err2 = _split_err(err2)

    if interrupt_trace:
        for err in (intr1, intr2):
            _show_err(err)
    if exc_trace:
        for err in (pipe1, err1):
            _show_err(err)
        for err in (pipe2, err2):
            # These have no traceback so say something first.
            _show_err(err, 'In final sys.stdout.flush():\n')

    if intr1 or intr2:
        ret = sigdie(signal.SIGINT)
    if pipe1 or pipe2:
        ret = sigdie(signal.SIGPIPE)
    sys.exit(ret)
