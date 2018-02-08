.PHONY: database backend frontend

all:
	cd backend && make

run:
	procwatch -c scripts/stack.ini

run-db:
	cd database && pivot -s schema -L debug -Q web

run-backend:
	cd backend && ./env/bin/python server.py

run-frontend:
	cd frontend && diecast

tail:
	tail -f logs/*

stop:
	test -f scripts/supervisord.pid
	kill `cat scripts/supervisord.pid`

shell:
	cd backend && make shell
