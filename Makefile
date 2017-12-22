.PHONY: database backend frontend

all:
	true

run:
	supervisord -c scripts/stack.ini
	make tail

tail:
	tail -f logs/*

stop:
	test -f scripts/supervisord.pid
	kill `cat scripts/supervisord.pid`
