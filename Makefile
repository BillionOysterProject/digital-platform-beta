.PHONY: database backend frontend
.EXPORT_ALL_VARIABLES:

PATH := "$(PATH):$(HOME)/go/bin:$(HOME)/bin:$(HOME)/.local/bin:$(HOME)/Library/Python/2.7/bin:"

all:
	cd backend && make

run:
	supervisord -c scripts/stack.ini

run-development:
	BOP_S3_PUBLIC_BUCKET=digital-platform-dev-files \
	PIVOT_ENV=development \
		supervisord -c scripts/stack.ini

run-production:
	BOP_S3_PUBLIC_BUCKET=digital-platform-prod-files \
	PIVOT_ENV=production \
		supervisord -c scripts/stack.ini

run-db:
	cd database && pivot -s schema -L debug -Q web

run-backend:
	cd backend && ./env/bin/python server.py

run-frontend:
	cd frontend && diecast

run-worker:
	cd backend && make run-worker

tail:
	tail -f logs/*

stop:
	test -f scripts/supervisord.pid
	kill `cat scripts/supervisord.pid`

shell:
	cd backend && make shell
