.PHONY: bop

all: env deps test

env:
	virtualenv env
	./env/bin/pip install pytest ipython

deps:
	./env/bin/pip install -r requirements.txt

test:
	./env/bin/py.test -x .

debug:
	PYTHONPATH=$(PWD) ./env/bin/python server.py

# run:

shell:
	./env/bin/ipython --config=shell.py
