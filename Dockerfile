FROM python:latest

RUN pip install python-binance

CMD [ "python", "/app/binance_bot.py" ]
