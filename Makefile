.PHONY: database backend frontend
.EXPORT_ALL_VARIABLES:

IMPERSONATE ?= bop-admin
DEBUG       ?= true
PATH        := "$(PATH):$(HOME)/go/bin:$(HOME)/bin:$(HOME)/.local/bin:$(HOME)/Library/Python/2.7/bin:"

all:
	cd backend && make

run:
	./scripts/stack.sh

run-development:
	BOP_S3_PUBLIC_BUCKET=digital-platform-dev-files \
	PIVOT_ENV=development ./scripts/stack.sh

run-production:
	BOP_S3_PUBLIC_BUCKET=digital-platform-prod-files \
	PIVOT_ENV=production ./scripts/stack.sh

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

tools-dist:
	GO111MODULE=on GOOS=darwin go build -o bin/darwin/pivot   -ldflags="-s -w" github.com/ghetzel/pivot/v3/pivot
	GO111MODULE=on GOOS=linux  go build -o bin/linux/pivot    -ldflags="-s -w" github.com/ghetzel/pivot/v3/pivot

	GOOS=darwin go build -o bin/darwin/diecast -ldflags="-s -w" github.com/ghetzel/diecast/diecast
	GOOS=linux  go build -o bin/linux/diecast  -ldflags="-s -w" github.com/ghetzel/diecast/diecast