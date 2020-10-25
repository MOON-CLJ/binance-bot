FROM python:latest

WORKDIR /binance-bot

RUN pip install python-binance retrying TA-Lib matplotlib numpy

CMD [ "bash" ]
