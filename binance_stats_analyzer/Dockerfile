FROM continuumio/miniconda3:latest

RUN apt-get update && apt-get install -y tzdata python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN pip3 install paho-mqtt pyyaml overrides seaborn matplotlib python-binance pandas darts
RUN pip3 install --upgrade mplfinance
RUN conda install -c conda-forge ta-lib

ARG USERNAME
ARG USER_ID
ARG GROUP_ID
ARG TZ
ENV TZ=${TZ}
RUN groupadd --gid ${GROUP_ID} ${USERNAME} && \
    adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} ${USERNAME}

USER ${USERNAME}
COPY ./binance_stats_analyzer /home/${USERNAME}/app
COPY ./common_utils /home/${USERNAME}/app/common_utils
WORKDIR /home/${USERNAME}/app
