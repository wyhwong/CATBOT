FROM continuumio/miniconda3:latest
ENV TZ=Asia/Hong_Kong

RUN apt-get update && apt-get install -y tzdata python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN pip3 install paho-mqtt pyyaml overrides seaborn matplotlib python-binance pandas darts
RUN pip3 install --upgrade mplfinance

RUN conda install -c conda-forge ta-lib

COPY ./binance_stats_analyzer /app
COPY ./common_utils /app/common_utils
WORKDIR /app
