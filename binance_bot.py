import sys
import logging
import time
import math

import config

from binance.client import Client
from binance.exceptions import BinanceAPIException

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


def calculate_profit_percentage(initial, final):
	percent = (float(final) - float(initial)) / float(initial) * 100
	return format(percent, '.2f')




client = Client(config.API_KEY, config.API_SECRET)

print("Welcome! type 'STOP' to stop")

while True:
	print("Enter a symbol.")
	sym = input('> ')

	if sym.lower() == "stop":
		exit()

	coin = sym[:-3]
	asset = sym[-3:]

	klines = client.get_historical_klines(sym, Client.KLINE_INTERVAL_1MINUTE, "1 min ago")
	most_recent = klines.pop()
	last_closing = most_recent[4]
	print("Last close price for {} was {}".format(sym, last_closing))

	balance = client.get_asset_balance(asset=asset)
	bitcoins = float(balance['free'])
	half_bitcoins = format(bitcoins / 2.0, '.8f')

	profit = calculate_price_target(last_closing)
	print("Your profit target is", profit)

	number_of_coins = find_quantity(half_bitcoins, last_closing)
	print("Your order will be for {} with {} {}".format(last_closing, number_of_coins, coin))

	try:
		print('Buying...')
		try:
			print("Buy method 1, three decimal places")
			client.order_limit_buy(symbol=sym, quantity=float(format(number_of_coins, '.3f')), price=last_closing)
		except:
			try:
				print("Method 1 failed.")
				print("Buy method 2, rounded coins")
				client.order_limit_buy(symbol=sym, quantity=round(number_of_coins), price=last_closing)
			except BinanceAPIException:
				try:
					print("Method 2 failed.")
					print("Buy method 3, rounded coins but minus one")
					client.order_limit_buy(symbol=sym, quantity=round(number_of_coins - 1), price=last_closing)
				except:
					print("Method 3 failed.")
					print("Buy method 4, 2 decimal places")
					client.order_limit_buy(symbol=sym, quantity=float(format(number_of_coins, '.2f')), price=last_closing)
		time.sleep(1)
		print("Order placed. Confirming...")
		order_confirm(sym)
		print("Selling... Might take a while...")
		try:
			print("Sell method float quantity 1")
			client.order_limit_sell(symbol=sym, quantity=float(format(number_of_coins, '.3f')), price=str(profit))
		except BinanceAPIException as e:
			print("Method 1 failed.")
			print("Sell method round quantity 2")
			if "LOT_SIZE" in e.message:
				try:
					client.order_limit_sell(symbol=sym, quantity=round(number_of_coins), price=str(profit))
				except BinanceAPIException as e:
					print("Method 2 failed.")
					print(e.message)
					print("Sell method round minus one quantity 3")
					try:
						client.order_limit_sell(symbol=sym, quantity=round(number_of_coins - 1), price=str(profit))
					except BinanceAPIException as e:
						print(e.message)
						print("Method 3 failed.")
						print("Sell method float quantity 4")
						client.order_limit_sell(symbol=sym, quantity=float(format(number_of_coins, '.2f')), price=str(profit))
			elif "PRICE_FILTER" in e.message:
				try:
					print("Method 2 failed.")
					print("Sell method 7 decimal places profit 3")
					profit = format(float(profit), '.7f')
					client.order_limit_sell(symbol=sym, quantity=float(format(number_of_coins, '.3f')), price=str(profit))
				except:
					try:
						print("Method 3 failed.")
						print("Sell method 6 decimal places profit 4")
						profit = format(float(profit), '.6f')
						client.order_limit_sell(symbol=sym, quantity=float(format(number_of_coins, '.3f')), price=str(profit))
					except BinanceAPIException:
						print("Method 4 failed.")
						print("Sell method float quantity 6 decimal places 5")
						profit = format(float(profit), '.6f')
						client.order_limit_sell(symbol=sym, quantity=float(format(number_of_coins, '.2f')), price=str(profit))
		print("Order placed. Confirming...")
		time.sleep(1)
		order_confirm(sym)
		percentage = calculate_profit_percentage(last_closing, profit)
		print("Congrats! You made a profit of {}%.".format(percentage))
	except BinanceAPIException as e:
		print(e.status_code)
		print(e.message)


class Trade:
	def __init__(self, option):
		logger.info(option)
		self.option = option
		self.client = Client(config.API_KEY, config.API_SECRET)
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
		self.filters = self.client.get_exchange_info()[""]

	def buy_order_confirm(self):
		cnt = 0
		while True:
			cnt += 1
			orders = self.client.get_open_orders(symbol=self.option.symbol)
			time.sleep(self.wait_time * min(cnt, 10))
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
			time.sleep(self.wait_time * min(cnt, 10))
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
		self.logger.info(
			'price:%.8f buyprice:%.8f sellprice:%.8f bid:%.8f ask:%.8f spread:%.2f Originalsellprice:%.8f' % (
				lastPrice, buyPrice, profitableSellingPrice, lastBid, lastAsk,
				spreadPerc, profitableSellingPrice - (lastBid * self.commision)))
		self.buy(buyPrice, self.buy_quantity)
		self.sell(profitableSellingPrice, self.buy_quantity)

	def buy(self, buyPrice, quantity):
		self.client.order_limit_buy(symbol=self.option.symbol, quantity=quantity, price=buyPrice)
		self.buy_order_confirm()

	def sell(self, profitableSellingPrice, quantity):
		client.order_limit_sell(symbol=self.option.symbol, quantity=quantity, price=profitableSellingPrice)
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
			quantity = self.amount / lastBid
		else:
			quantity = minNotional / lastBid * 1.1

		quantity = self.format_quantity(quantity, stepSize)
		notional = lastBid * float(quantity)

		if quantity < minQty:
			logger.error('Invalid quantity, minQty: %.8f (u: %.8f)' % (minQty, quantity))
			sys.exit(1)

		if lastPrice < minPrice:
			self.logger.error('Invalid price, minPrice: %.8f (u: %.8f)' % (minPrice, lastPrice))
			sys.exit(1)

		if notional < minNotional:
			self.logger.error('Invalid notional, minNotional: %.8f (u: %.8f)' % (minNotional, notional))
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

    option = parser.parse_args()

    # Get start
    t = Trade(option)
    t.run()
