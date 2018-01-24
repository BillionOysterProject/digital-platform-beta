.PHONY: database backend frontend

all:
	cd backend && make

run:
	procwatch -c scripts/stack.ini

tail:
	tail -f logs/*

stop:
	test -f scripts/supervisord.pid
	kill `cat scripts/supervisord.pid`

shell:
	cd backend && make shell
