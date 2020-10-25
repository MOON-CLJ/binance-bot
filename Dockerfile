FROM python:latest

WORKDIR /binance-bot

RUN pip install python-binance retrying

CMD [ "bash" ]
