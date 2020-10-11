import sys
import logging
import time
import math
import argparse

from binance.client import Client
from binance.exceptions import BinanceAPIException

logger = logging.getLogger(__name__)

API_SECRET = 'ENTER-YOUR-SECRET-KEY-HERE'
API_KEY = 'ENTER-YOUR-API-HERE'


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


"""
klines = client.get_historical_klines(sym, Client.KLINE_INTERVAL_1MINUTE, "1 min ago")
most_recent = klines.pop()
last_closing = most_recent[4]
"""


class Trade:
    def __init__(self, option):
        logger.info(option)
        self.option = option
        self.client = Client(API_KEY, API_SECRET)
        self.commision = 0.0005

        self.filters = None
        self.increasing = self.option.increasing
        self.decreasing = self.option.decreasing

        self.tick_size = None
        self.step_size = None
        self.min_price = None
        self.buy_quantity = None

    def calculate_price_target(self, lastBid):
        return lastBid + (lastBid * self.option.profit / 100) + (lastBid * self.commision)

    def get_exchange_info(self):
        exchange_info = self.client.get_exchange_info()
        for symbol_info in exchange_info["symbols"]:
            if symbol_info["symbol"] == self.option.symbol:
                self.filters = symbol_info["filters"]

    def buy_order_confirm(self):
        cnt = 0
        while True:
            cnt += 1
            orders = self.client.get_open_orders(symbol=self.option.symbol)
            time.sleep(self.option.wait_time * min(cnt, 10))
            if not orders:
                return
            if all([order['status'] == 'FILLED' for order in orders if order['side'] == 'BUY']):
                logger.info('Buy order filled')
                return
            logger.info(orders)

        logger.info("Buy order confirmed!")

    def sell_order_confirm(self):
        cnt = 0
        while True:
            cnt += 1
            orders = self.client.get_open_orders(symbol=self.option.symbol)
            time.sleep(self.option.wait_time * min(cnt, 10))
            if not orders:
                return
            if all([order['status'] == 'FILLED' for order in orders if order['side'] == 'SELL']):
                logger.info('Sell order filled')
                return
            logger.info(orders)

        logger.info("Sell order is confirmed!")

    def action(self):
        lastPrice = float(self.client.get_ticker(self.option.symbol)["lastPrice"])
        assert lastPrice > 0, "lastPrice must > 0"

        order_book = self.client.get_order_book(self.option.symbol)
        bids = order_book["bids"]
        asks = order_book["asks"]
        lastBid = float(bids[0][0])
        lastAsk = float(asks[0][0])
        assert lastBid > 0, "lastBid must > 0"
        assert lastAsk > 0, "lastAsk must > 0"

        # Target buy price, add little increase #87
        buyPrice = lastBid + self.increasing
        profitableSellingPrice = self.format_price(self.calculate_price_target(lastBid), formatter=math.ceil)
        if self.option.buyprice > 0 and buyPrice > self.option.buyprice:
            raise Exception(f"buyPrice {buyPrice} more than {self.option.buyprice}")

        spreadPerc = (lastAsk / lastBid - 1) * 100.0
        logger.info(
            'price:%.8f buyprice:%.8f sellprice:%.8f bid:%.8f ask:%.8f spread:%.2f Originalsellprice:%.8f' % (
                lastPrice, buyPrice, profitableSellingPrice, lastBid, lastAsk,
                spreadPerc, profitableSellingPrice - (lastBid * self.commision)))
        self.buy(buyPrice, self.buy_quantity)
        self.sell(profitableSellingPrice, self.buy_quantity)

    def buy(self, buyPrice, quantity):
        self.client.order_limit_buy(symbol=self.option.symbol, quantity=quantity, price=buyPrice)
        self.buy_order_confirm()

    def sell(self, profitableSellingPrice, quantity):
        self.client.order_limit_sell(symbol=self.option.symbol, quantity=quantity, price=profitableSellingPrice)
        self.sell_order_confirm()

    def format_quantity(self, quantity):
        return float(self.step_size * math.floor(float(quantity) / self.step_size))

    def format_price(self, price, formatter=math.floor):
        return self.min_price + float(self.tick_size * formatter(float(price - self.min_price) / self.tick_size))

    def validate(self):
        self.get_exchange_info()
        order_book = self.client.get_order_book(self.option.symbol)
        bids = order_book["bids"]
        lastBid = float(bids[0][0])

        lastPrice = float(self.client.get_ticker(self.option.symbol)["lastPrice"])

        minQty = float(self.filters['LOT_SIZE']['minQty'])
        minPrice = float(self.filters['PRICE_FILTER']['minPrice'])
        minNotional = float(self.filters['MIN_NOTIONAL']['minNotional'])

        # stepSize defines the intervals that a quantity/icebergQty can be increased/decreased by.
        stepSize = float(self.filters['LOT_SIZE']['stepSize'])

        # tickSize defines the intervals that a price/stopPrice can be increased/decreased by
        tickSize = float(self.filters['PRICE_FILTER']['tickSize'])
        if tickSize < self.increasing:
            self.increasing = tickSize
        if tickSize < self.decreasing:
            self.decreasing = tickSize

        # set
        self.tick_size = tickSize
        self.step_size = stepSize
        self.min_price = minPrice

        if self.option.quantity > 0:
            quantity = self.option.quantity
        elif self.option.amount > 0:
            quantity = self.option.amount / lastBid
        else:
            quantity = minNotional / lastBid * 1.1

        quantity = self.format_quantity(quantity)
        notional = lastBid * float(quantity)

        if quantity < minQty:
            logger.error('Invalid quantity, minQty: %.8f (u: %.8f)' % (minQty, quantity))
            sys.exit(1)

        if lastPrice < minPrice:
            logger.error('Invalid price, minPrice: %.8f (u: %.8f)' % (minPrice, lastPrice))
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
    parser.add_argument('--amount', type=float, help='Buy/Sell Amount (Ex: 0.002 BTC)', default=0)
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', required=True)
    parser.add_argument('--profit', type=float, help='Target Profit', default=1.3)

    parser.add_argument('--increasing', type=float, help='Buy Price +Increasing (0.00000001)', default=0.00000001)
    parser.add_argument('--decreasing', type=float, help='Sell Price -Decreasing (0.00000001)', default=0.00000001)

    parser.add_argument('--wait_time', type=float, help='Wait Time (seconds)', default=0.7)

    parser.add_argument('--buyprice', type=float, help='Buy Price (Price is less than equal <=)', default=0)
    parser.add_argument('--sellprice', type=float, help='Sell Price (Price is greater than equal >=)', default=0)

    # Get start
    t = Trade(parser.parse_args())
    t.run()
