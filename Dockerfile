FROM python:3-alpine

RUN apk upgrade \
    && apk add gcc
RUN pip install python-binance

CMD [ "python", "/app/binance_bot.py" ]
