export DOCKER_BUILDKIT=1

build:
	docker-compose build

start:
	docker-compose -f docker-compose.yml up

clean:
	docker-compose -f docker-compose.yml down --remove-orphans
