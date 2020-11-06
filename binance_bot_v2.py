import sys
import logging
import logging.handlers
import time
import datetime
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

        self.min_quantity = None

        self.history = {}
        for interval in self.option.interval.split(","):
            self.history[interval] = {
                "active_buy": False,
                "last_buy_quantity": None,
                "last_buy_price": None,
                "last_action_datetime": None,
            }

    def get_symbol_info(self):
        symbol_info = self.client.get_symbol_info(symbol=self.option.symbol)
        logger.info(symbol_info)
        self.baseAssetPrecision = symbol_info["baseAssetPrecision"]
        assert self.baseAssetPrecision >= 4
        self.filters = {filter["filterType"]: filter for filter in symbol_info["filters"]}

    def format_price(self, price, formatter=math.floor):
        return self.min_price + float(self.tick_size * formatter(float(price - self.min_price) / self.tick_size))

    def action(self):
        for interval in self.option.interval.split(","):
            interval_last_data = self.history[interval]
            klines = retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)(self.client.get_klines)(symbol=self.option.symbol, interval=interval, limit=1000)
            klines = klines[:-1]  # 去掉最后一个
            macd_strategy = Strategy('MACD', 'CROSS', self.option.symbol, interval, klines)
            strategy_result = macd_strategy.getStrategyResult()
            if not strategy_result:
                continue
            if interval_last_data["last_action_datetime"] is None:
                interval_last_data["last_action_datetime"] = strategy_result[-1][0]
                logger.info("init interval:%s last_action_datetime:%s", interval, interval_last_data["last_action_datetime"].isoformat())
            if strategy_result[-1][0] > interval_last_data["last_action_datetime"]:
                if strategy_result[-1][3] == "BUY":
                    logger.info("** " * 10)
                    if interval_last_data["active_buy"] is False:
                        interval_last_data["last_buy_quantity"], interval_last_data["last_buy_price"] = self.order_market_buy()
                        interval_last_data["active_buy"] = True
                        interval_last_data["last_action_datetime"] = strategy_result[-1][0]
                        logger.info("buy interval:%s last_action_datetime:%s", interval, interval_last_data["last_action_datetime"].isoformat())
                    else:
                        logger.info("!! " * 10)
                        logger.info("not buy interval:%s price:%s", interval, strategy_result[-1][4])
                if strategy_result[-1][3] == "SELL":
                    logger.info("-- " * 10)
                    if interval_last_data["active_buy"] is True:
                        if float(strategy_result[-1][4]) < interval_last_data["last_buy_price"] * 1.003:
                            logger.info("sell stop loss")
                            profitableSellingPrice = interval_last_data["last_buy_price"] * 1.003
                        else:
                            logger.info("sell profitable")
                            profitableSellingPrice = float(strategy_result[-1][4])
                        profitableSellingPrice = self.format_price(profitableSellingPrice, formatter=math.ceil)

                        self.order_limit_sell(interval_last_data["last_buy_quantity"], profitableSellingPrice)
                        interval_last_data["active_buy"] = False
                        interval_last_data["last_action_datetime"] = strategy_result[-1][0]
                        logger.info("sell interval:%s last_action_datetime:%s", interval, interval_last_data["last_action_datetime"].isoformat())
                    else:
                        logger.info("!! " * 10)
                        logger.info("not sell interval:%s price:%s", interval, strategy_result[-1][4])

    def order_market_buy(self):
        quantity = self.min_quantity * self.option.above_multiple
        quantity = self.format_quantity(quantity)
        logger.info("buy quantity:%s", quantity)
        order = self.client.order_market_buy(symbol=self.option.symbol, quantity=quantity)
        logger.info("order %r", order)
        if len(order["fills"]) > 1:
            price = sum([float(i["price"]) * float(i["qty"]) for i in order["fills"]]) / sum([float(i["qty"]) for i in order["fills"]])
        else:
            price = float(order["fills"][0]["price"])
        logger.info("last_buy_price:%r", price)
        return quantity, price

    def order_limit_sell(self, quantity, profitableSellingPrice):
        profitableSellingPriceStr = "{:0.0{}f}".format(profitableSellingPrice, self.baseAssetPrecision-2)
        logger.info("sell quantity:%s", quantity)
        logger.info("profitableSellingPrice:%r", profitableSellingPriceStr)
        order = retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)(self.client.order_limit_sell)(symbol=self.option.symbol, quantity=quantity, price=profitableSellingPriceStr)
        logger.info("order %r", order)

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
        minPrice = float(self.filters['PRICE_FILTER']['minPrice'])
        minNotional = float(self.filters['MIN_NOTIONAL']['minNotional'])

        # stepSize defines the intervals that a quantity/icebergQty can be increased/decreased by.
        stepSize = float(self.filters['LOT_SIZE']['stepSize'])

        # tickSize defines the intervals that a price/stopPrice can be increased/decreased by
        tickSize = float(self.filters['PRICE_FILTER']['tickSize'])

        # set
        self.tick_size = tickSize
        self.step_size = stepSize
        self.min_price = minPrice

        quantity = minNotional / lastBid

        quantity = self.format_quantity(quantity)
        notional = lastBid * quantity

        if quantity < minQty:
            logger.error('Invalid quantity, minQty: %.8f (u: %.8f)' % (minQty, quantity))
            sys.exit(1)

        if notional < minNotional:
            logger.error('Invalid notional, minNotional: %.8f (u: %.8f)' % (minNotional, notional))
            sys.exit(1)

        # set
        self.min_quantity = quantity

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
    parser.add_argument('--above_multiple', type=float, help='Buy/Sell multiple', default=1.2)
    parser.add_argument('--below_multiple', type=float, help='Buy/Sell multiple', default=3)
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', required=True)
    parser.add_argument('--interval', type=str, help='interval', required=True)
    parser.add_argument('--wait_time', type=float, help='Wait Time (seconds)', default=10)

    # Get start
    t = Trader(parser.parse_args())
    t.run()
