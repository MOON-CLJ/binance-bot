FROM python:latest

WORKDIR /binance-bot

RUN pip install python-binance retrying matplotlib numpy

RUN http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && cd ta-lib/ && ./configure --prefix=/usr && make && make install && pip install TA-Lib

CMD [ "bash" ]
