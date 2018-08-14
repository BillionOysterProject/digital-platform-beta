.PHONY: database backend frontend
.EXPORT_ALL_VARIABLES:

PATH := "$(PATH):$(HOME)/go/bin:$(HOME)/bin:$(HOME)/.local/bin:$(HOME)/Library/Python/2.7/bin:"

all:
	cd backend && make

run-pre:
	test -d logs || mkdir logs

run: run-pre
	./backend/env/bin/supervisord -c scripts/stack.ini

run-development: run-pre
	BOP_S3_PUBLIC_BUCKET=digital-platform-dev-files \
	PIVOT_ENV=development ./backend/env/bin/supervisord -c scripts/stack.ini

run-production: run-pre
	BOP_S3_PUBLIC_BUCKET=digital-platform-prod-files \
	PIVOT_ENV=production ./backend/env/bin/supervisord -c scripts/stack.ini

run-db: run-pre
	cd database && pivot -s schema -L debug -Q web

run-backend: run-pre
	cd backend && ./env/bin/python server.py

run-frontend: run-pre
	cd frontend && diecast

run-worker: run-pre
	cd backend && make run-worker

tail:
	tail -f logs/*

stop:
	test -f scripts/supervisord.pid
	kill `cat scripts/supervisord.pid`

shell:
	cd backend && make shell
