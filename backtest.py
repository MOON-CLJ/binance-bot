import argparse

from binance.client import Client

import config
from macd_strategy import Strategy


class Backtest:
    def __init__(self, starting_amount, start_datetime, end_datetime, strategy):
        # Starting amount
        self.start = starting_amount
        # Number of trades
        self.num_trades = 0
        # Number of profitable trades
        self.profitable_trades = 0
        # Running amount
        self.amount = self.start
        # Start of desired interval
        self.startTime = start_datetime
        # End of desired interval
        self.endTime = end_datetime
        # Strategy object
        self.strategy = strategy
        # Trading pair
        self.pair = self.strategy.getPair()
        # Trading interval
        self.interval = self.strategy.getInterval()
        # Outputs the trades exectued
        self.trades = []
        # Runs the backtest
        self.results = self.runBacktest()

    def runBacktest(self):
        amount = self.start
        klines = self.strategy.getKlines()
        time = self.strategy.getTime()
        point_finder = 0
        strategy_result = self.strategy.getStrategyResult()
        # Finds the first cross point within the desired backtest interval
        while point_finder <= len(strategy_result) - 1 and strategy_result[point_finder][0] < self.startTime:
            point_finder += 1
        # Initialize to not buy
        active_buy = False
        buy_price = 0
        # Runs through each kline
        for i in range(len(klines)):
            if point_finder > len(strategy_result) - 1:
                break
            # If timestamp is in the interval, check if strategy has triggered a buy or sell
            if time[i] >= self.startTime and time[i] <= self.endTime:
                if (time[i] == strategy_result[point_finder][0]):
                    if strategy_result[point_finder][3] == 'BUY':
                        assert active_buy is False
                        active_buy = True
                        buy_price = float(strategy_result[point_finder][4])
                        self.trades.append([strategy_result[point_finder][0], 'BUY', buy_price])
                    if strategy_result[point_finder][3] == 'SELL' and active_buy == True:
                        active_buy = False
                        bought_amount = amount / buy_price
                        self.num_trades += 1
                        if (float(strategy_result[point_finder][4]) > buy_price):
                            self.profitable_trades += 1
                        amount = bought_amount * float(strategy_result[point_finder][4])
                        self.trades.append([strategy_result[point_finder][0], 'SELL', float(strategy_result[point_finder][4])])
                    point_finder += 1
        self.amount = amount

    '''
    Prints the results of the backtest
    '''

    def printResults(self):
        print("Trading Pair: " + self.pair)
        print("Interval: " + self.interval)
        print("Ending amount: " + str(self.amount))
        print("Number of Trades: " + str(self.num_trades))
        profitable = self.profitable_trades / self.num_trades * 100
        print("Percentage of Profitable Trades: " + str(profitable) + "%")
        percent = self.amount / self.start * 100
        print(str(percent) + "% of starting amount")
        for entry in self.trades:
            print(entry[1] + " at " + str(entry[2]) + " when " + entry[0].isoformat())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', required=True)
    parser.add_argument('--interval', type=str, help='interval', default="1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M")
    option = parser.parse_args()

    client = Client(config.API_KEY, config.API_SECRET)
    symbol = option.symbol
    interval = option.interval
    intervals = interval.split(",")
    if len(intervals) == 1:
        klines = client.get_klines(symbol=symbol, interval=interval)
        macd_strategy = Strategy('MACD', 'CROSS', symbol, interval, klines)
        time = macd_strategy.getTime()
        macd_backtest = Backtest(10000, time[0], time[len(time) - 1], macd_strategy)
        if macd_backtest.num_trades > 0:
            macd_backtest.printResults()
    else:
        macd_backtests = []
        for interval in intervals:
            klines = client.get_klines(symbol=symbol, interval=interval)
            macd_strategy = Strategy('MACD', 'CROSS', symbol, interval, klines)
            time = macd_strategy.getTime()
            macd_backtest = Backtest(10000, time[0], time[len(time) - 1], macd_strategy)
            macd_backtests.append(macd_backtest)
            """
            if macd_backtest.amount - 75 * macd_backtest.num_trades > 11000:
                macd_strategy.plotIndicator()
            """
        macd_backtests = sorted(macd_backtests, key=lambda x: x.amount - 75 * x.num_trades)
        for macd_backtest in macd_backtests[-3:]:
            if macd_backtest.num_trades > 0:
                macd_backtest.printResults()
