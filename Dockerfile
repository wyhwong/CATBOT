FROM python:3.11-slim-buster

RUN python3 -m pip install --upgrade pip

# For common utils, slackbot, stats analyzer, text analyzer
RUN pip3 install paho-mqtt pyyaml==6.0.1 overrides==7.4.0 && \
    pip3 install slack_bolt==1.18.0 pandas==2.0.3 && \
    pip3 install python-binance==1.0.19 darts==0.25.0 seaborn==0.12.2 matplotlib==3.7.2 && \
    pip3 install --upgrade mplfinance==0.12.10b0 && \
    pip3 install torch==2.0.1 transformers==4.32.1 requests==2.31.0 bs4==0.0.1 tweepy==4.14.0 praw==7.7.1 p_tqdm==1.4.0

ARG USERNAME
ARG USER_ID
ARG GROUP_ID
ARG TZ
ENV TZ=${TZ}
RUN groupadd --gid ${GROUP_ID} ${USERNAME} && \
    adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app
