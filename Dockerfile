FROM python:latest

WORKDIR /binance-bot

RUN pip install -r requirement.txt

CMD [ "bash" ]
