FROM python:latest

RUN pip install python-binance retrying

CMD [ "python", "/app/binance_bot.py" ]
