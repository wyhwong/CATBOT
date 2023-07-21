FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y tzdata python3 python3-pip -y
RUN pip3 install --upgrade pip
RUN pip3 install paho-mqtt pyyaml overrides torch transformers requests bs4 tweepy praw p_tqdm pandas

ARG USERNAME
ARG USER_ID
ARG GROUP_ID
ARG TZ
ENV TZ=${TZ}
RUN groupadd --gid ${GROUP_ID} ${USERNAME} && \
    adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} ${USERNAME}

USER ${USERNAME}
COPY ./text_analyzer /home/${USERNAME}/app
COPY ./common_utils /home/${USERNAME}/app/common_utils
WORKDIR /home/${USERNAME}/app
