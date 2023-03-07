FROM continuumio/miniconda3:latest
RUN TZ=Asia/Hong_Kong

RUN apt-get update && apt-get install -y tzdata python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN pip3 install paho-mqtt pyyaml overrides seaborn matplotlib python-binance pandas darts
RUN pip3 install --upgrade mplfinance

RUN conda install -c conda-forge ta-lib

COPY ../common_utils /app/
COPY ../common_configs /app/
COPY . /app

WORKDIR /app
