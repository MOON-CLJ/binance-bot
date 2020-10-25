FROM python:latest

WORKDIR /binance-bot

RUN pip install requirement.txt

CMD [ "bash" ]
