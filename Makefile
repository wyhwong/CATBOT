export DOCKER_BUILDKIT=1

mode?=dev
data_dir?=./data

build:
	DATA_DIR=${data_dir} \
	docker-compose build

start:
	DATA_DIR=${data_dir} \
	docker-compose -f docker-compose.yml -f docker-compose-${mode}.yml up -d

clean:
	docker-compose -f docker-compose.yml down --remove-orphans
