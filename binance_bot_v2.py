import sys
import logging
import logging.handlers
import time
import math
import argparse

import config

from binance.client import Client
from retrying import retry
from macd_strategy import Strategy

logger = logging.getLogger(__name__)


def setup_logger(symbol):
    format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    formatter = logging.Formatter(format)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    log_file = symbol + '.trade.log'
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file, when='midnight', backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class Trader:
    def __init__(self, option):
        setup_logger(option.symbol)
        logger.info(option)

        self.option = option
        self.client = Client(config.API_KEY, config.API_SECRET)
        self.commision = 0.0075 * 2

        self.filters = None
        self.baseAssetPrecision = None

        self.buy_quantity = None

    def get_symbol_info(self):
        symbol_info = self.client.get_symbol_info(symbol=self.option.symbol)
        logger.info(symbol_info)
        self.baseAssetPrecision = symbol_info["baseAssetPrecision"]
        assert self.baseAssetPrecision >= 4
        self.filters = {filter["filterType"]: filter for filter in symbol_info["filters"]}

    def action(self):
        klines = retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)(self.client.get_klines)(symbol=self.option.symbol, interval=self.option.interval)
        macd_strategy = Strategy('MACD', 'CROSS', self.option.symbol, self.option.interval, klines)
        time = macd_strategy.getTime()
        strategy_result = macd_strategy.getStrategyResult()
        active_buy = False
        if time[-1] == strategy_result[-1][0]:
            if strategy_result[-1][3] == "BUY":
                assert active_buy is False
                active_buy = True
                self.buy()
            if strategy_result[-1][3] == "SELL":
                assert active_buy is True
                active_buy = False
                self.sell()

    def buy(self):
        try:
            logger.info("buy %s", self.buy_quantity)
            return
            order = self.client.order_market_buy(symbol=self.option.symbol, quantity=self.buy_quantity)
            return order
        except Exception:
            logger.exception("buy failed")

    def sell(self):
        try:
            logger.info("sell %s", self.buy_quantity)
            return
            order = self.client.order_market_sell(symbol=self.option.symbol, quantity=self.buy_quantity)
            return order
        except Exception:
            logger.exception("sell failed")

    def format_quantity(self, quantity):
        assert 0 < self.step_size <= 0.1
        quantity = self.step_size * int(math.ceil(quantity / self.step_size))
        roundn = int(math.fabs(math.floor(math.log(self.step_size, 10))))
        quantity = round(quantity, roundn)
        return quantity

    def validate(self):
        self.get_symbol_info()
        order_book = self.client.get_order_book(symbol=self.option.symbol)
        bids = order_book["bids"]
        lastBid = float(bids[0][0])

        minQty = float(self.filters['LOT_SIZE']['minQty'])
        minNotional = float(self.filters['MIN_NOTIONAL']['minNotional'])

        # stepSize defines the intervals that a quantity/icebergQty can be increased/decreased by.
        stepSize = float(self.filters['LOT_SIZE']['stepSize'])

        # set
        self.step_size = stepSize

        if self.option.quantity > 0:
            quantity = self.option.quantity
        else:
            quantity = minNotional / lastBid * 1.1 * self.option.multiple

        quantity = self.format_quantity(quantity)
        notional = lastBid * quantity

        if quantity < minQty:
            logger.error('Invalid quantity, minQty: %.8f (u: %.8f)' % (minQty, quantity))
            sys.exit(1)

        if notional < minNotional:
            logger.error('Invalid notional, minNotional: %.8f (u: %.8f)' % (minNotional, notional))
            sys.exit(1)

        # set
        self.buy_quantity = quantity

    def run(self):
        self.validate()
        while True:
            try:
                self.action()
            except Exception:
                logger.exception("failed")
                time.sleep(self.option.wait_time * 10)
            time.sleep(self.option.wait_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quantity', type=float, help='Buy/Sell Quantity', default=0)
    parser.add_argument('--multiple', type=float, help='Buy/Sell Quantity', default=1)
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', required=True)
    parser.add_argument('--interval', type=str, help='interval', required=True)

    # Get start
    t = Trader(parser.parse_args())
    t.run()
