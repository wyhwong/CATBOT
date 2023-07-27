export DOCKER_BUILDKIT=1

export USERNAME?=$(shell whoami)
export USER_ID?=$(shell id -u)
export GROUP_ID?=$(shell id -g)
export TZ?=Asia/Hong_Kong
export MODE?=dev
export DATA_DIR?=./data
export VERSION?=devel
export LOGLEVEL?=20

# Analyzer
export ANALYSIS_INTERVAL_IN_SECOND?=300
export ANALYSIS_WAITTIME?=30
export TEXT_INFERENCE_PRETRAINED?=

# Binance
export BINANCE_API_KEY?=
export BINANCE_API_SECRET?=

# Slack
export SLACK_TOKEN?=
export SLACK_APP_TOKEN?=
export SLACK_USER_ID?=

# Reddit
export REDDIT_CLIENT_ID?=
export REDDIT_CLIENT_SECRET?=
export REDDIT_USER_AGENT?=

# Twitter
export TWEEPY_CONSUMER_KEY?=
export TWEEPY_CONSUMER_SECRET?=
export TWEEPY_ACCESS_TOKEN?=
export TWEEPY_ACCESS_TOKEN_SECRET?=

build:
	mkdir -p ${DATA_DIR}
	docker-compose build

start:
	@echo "Running in ${MODE} mode"
	docker-compose up -d

clean:
	docker-compose down --remove-orphans
