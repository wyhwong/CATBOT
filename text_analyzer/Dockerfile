FROM ubuntu:20.04
RUN TZ=Asia/Hong_Kong
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y tzdata python3 python3-pip -y
RUN pip3 install --upgrade pip

RUN pip3 install paho-mqtt pyyaml overrides torch transformers
# COPY ../utils/* /app/common_utils/
# COPY ../config/* /app/common_config/
# COPY ./binance /app

WORKDIR /app
