"""
Test SIGINT handling.
"""

import os
import signal
import sys
import time

def autotest():
    """
    Automated test: kill child, make sure it dies of SIGINT
    """
    pid = os.fork()
    if pid == 0:
        # child, sleep for 1 second, let parent kill us cleanly
        time.sleep(1)
        sys.exit(1)

    #print('interrupting child (pid %d) ...' % pid)
    # Need to give the child process a moment to return from fork,
    # lest the signal never arrive.  (Is this a kernel bug?)
    time.sleep(0.1)
    os.kill(pid, signal.SIGINT)
    while True:
        cpid, status = os.wait()
        if cpid == pid:
            break
        print('collected stray child pid %d while waiting for %d' %
            (cpid, pid))

    if os.WIFSIGNALED(status):
        sig = os.WTERMSIG(status)
        if sig == signal.SIGINT:
            return True, 'child correctly died of SIGINT'
        else:
            return False, 'child died of signal %d instead of SIGINT' % sig
    else:
        return (False,
                'child exited with status %d, expected to die of SIGINT' %
                    os.WEXITSTATUS(status))

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-a':
        # automated test
        ok, text = autotest()
        if ok:
            print('PASS: %s' % text)
            sys.exit(0)
        print('FAIL: %s' % text)
    else:
        print('press ^C now (within 5 seconds)')
        time.sleep(5)
        print('apparently failed, or ^C too late')
    sys.exit(1)

if __name__ == '__main__':
    from start import start
    start(main)
