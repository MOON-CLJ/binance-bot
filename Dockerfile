FROM python:3-alpine

RUN pip install python-binance

CMD [ "python", "/app/binance_bot.py" ]
