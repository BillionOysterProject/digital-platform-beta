.PHONY: bop

all: env deps test

env:
	which virtualenv || pip install --user virtualenv
	virtualenv env
	./env/bin/pip install pytest ipython

deps:
	./env/bin/pip install -r requirements.txt

test:
	./env/bin/py.test -x .

debug:
	PYTHONPATH=$(PWD) ./env/bin/python server.py

run:
	WSGI=1 PYTHONPATH=$(PWD) ./env/bin/python server.py

shell:
	./env/bin/ipython --config=shell.py


run-worker:
	./env/bin/python worker.py
