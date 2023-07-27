FROM python:3.11-slim-buster

RUN python3 -m pip install --upgrade pip
# For Slackbot
RUN pip3 install paho-mqtt pyyaml overrides slack_bolt pandas

# For Binance Stats Analyzer
RUN pip3 install python-binance darts seaborn matplotlib
RUN pip3 install --upgrade mplfinance

# For Text Analyzer
RUN pip3 install torch transformers requests bs4 tweepy praw p_tqdm

ARG USERNAME
ARG USER_ID
ARG GROUP_ID
ARG TZ
ENV TZ=${TZ}
RUN groupadd --gid ${GROUP_ID} ${USERNAME} && \
    adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app
