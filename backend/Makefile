.PHONY: bop

all: env deps test

env:
	python3 -m virtualenv --version || pip3 install --user virtualenv
	python3 -m virtualenv env
	./env/bin/pip3 install pytest ipython

deps:
	./env/bin/pip3 install -r requirements.txt

test:
	./env/bin/py.test -x .

debug:
	PYTHONPATH=$(PWD) ./env/bin/python3 server.py

run:
	WSGI=1 PYTHONPATH=$(PWD) ./env/bin/python3 server.py

shell:
	./env/bin/ipython --config=shell.py


run-worker:
	./env/bin/python3 worker.py
