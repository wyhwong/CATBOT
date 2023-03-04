export DOCKER_BUILDKIT=1

mode?=dev

build:
	docker-compose build

start:
	docker-compose -f docker-compose.yml -f docker-compose-${mode}.yml up -d

clean:
	docker-compose -f docker-compose.yml down --remove-orphans
