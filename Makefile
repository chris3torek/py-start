PYTHON=	python2

all: bpipe inttest trap

bpipe:
	@echo "expect 2 lines of output and no broken-pipe spewage"
	${PYTHON} bpipe.py | head -2

inttest:
	@rm -f inttest.core
	${PYTHON} inttest.py -a
	test ! -f inttest.core

trap:
	@rm -f trap.core
	@echo "Expect this to detect an internal error and leave a core file"
	${PYTHON} trap.py
	test -f trap.core
	rm -f trap.core

clean:
	rm -rf *.pyc __pycache__ *.core
