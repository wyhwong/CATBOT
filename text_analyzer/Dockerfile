FROM ubuntu:20.04
RUN TZ=Asia/Hong_Kong
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y tzdata python3 python3-pip -y
RUN pip3 install --upgrade pip
RUN pip3 install paho-mqtt pyyaml overrides torch transformers requests bs4

COPY ../common_utils /app/
COPY ../common_configs /app/
COPY ./text_analyzer /app

WORKDIR /app
