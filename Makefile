SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

default: docker-build

all:

docker-build:
	docker build -f ./src/logger_server/Dockerfile -t "tp1_logger_server:latest" .
	docker build -f ./src/query_server/Dockerfile -t "tp1_query_server:latest" .
	docker build -f ./src/client/Dockerfile -t "tp1_client:latest" .
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-build

docker-compose-up: docker-build
	docker-compose up --build
.PHONY: docker-compose-up

docker-compose-down:
	docker-compose stop -t 1000
	docker-compose down
.PHONY: docker-compose-down

docker-compose-logs:
	docker-compose logs -f
.PHONY: docker-compose-logs
