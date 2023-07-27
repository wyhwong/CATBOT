FROM python:3.11-slim-buster

RUN python3 -m pip install --upgrade pip

# For common utils, slackbot, stats analyzer, text analyzer
RUN pip3 install paho-mqtt pyyaml overrides && \
    pip3 install slack_bolt pandas && \
    pip3 install python-binance darts seaborn matplotlib && \
    pip3 install --upgrade mplfinance && \
    pip3 install torch transformers requests bs4 tweepy praw p_tqdm

ARG USERNAME
ARG USER_ID
ARG GROUP_ID
ARG TZ
ENV TZ=${TZ}
RUN groupadd --gid ${GROUP_ID} ${USERNAME} && \
    adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app
