import argparse

from binance.client import Client
import talib as ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import config


class Trader:
    def __init__(self):
        self.client = Client(config.API_KEY, config.API_SECRET)


class Strategy:

    def __init__(self, indicator_name, strategy_name, pair, interval, klines):
        # Name of indicator
        self.indicator = indicator_name
        # Name of strategy being used
        self.strategy = strategy_name
        # Trading pair
        self.pair = pair
        # Trading interval
        self.interval = interval
        # Kline data for the pair on given interval
        self.klines = klines
        # Calculates the indicator
        self.indicator_result = self.calculateIndicator()
        # Uses the indicator to run strategy
        self.strategy_result = self.calculateStrategy()

    '''
    Calculates the desired indicator given the init parameters
    '''

    def calculateIndicator(self):
        if self.indicator == 'MACD':
            close = [float(entry[4]) for entry in self.klines]
            close_array = np.asarray(close)

            macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
            return [macd, macdsignal, macdhist]

        else:
            return None

    '''
    Runs the desired strategy given the indicator results
    '''

    def calculateStrategy(self):
        if self.indicator == 'MACD':

            if self.strategy == 'CROSS':
                open_time = [int(entry[0]) for entry in self.klines]
                new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                self.time = new_time
                crosses = []
                macdabove = False
                # Runs through each timestamp in order
                for i in range(len(self.indicator_result[0])):
                    if np.isnan(self.indicator_result[0][i]) or np.isnan(self.indicator_result[1][i]):
                        pass
                    # If both the MACD and signal are well defined, we compare the 2 and decide if a cross has occured
                    else:
                        if self.indicator_result[0][i] > self.indicator_result[1][i]:
                            if macdabove == False:
                                macdabove = True
                                # Appends the timestamp, MACD value at the timestamp, color of dot, buy signal, and the buy price
                                cross = [new_time[i], self.indicator_result[0][i], 'go', 'BUY', self.klines[i][4]]
                                crosses.append(cross)
                        else:
                            if macdabove == True:
                                macdabove = False
                                # Appends the timestamp, MACD value at the timestamp, color of dot, sell signal, and the sell price
                                cross = [new_time[i], self.indicator_result[0][i], 'ro', 'SELL', self.klines[i][4]]
                                crosses.append(cross)
                return crosses

            else:
                return None
        else:
            return None

    '''
    Getter for the strategy result
    '''

    def getStrategyResult(self):
        return self.strategy_result

    '''
    Getter for the klines
    '''

    def getKlines(self):
        return self.klines

    '''
    Getter for the trading pair
    '''

    def getPair(self):
        return self.pair

    '''
    Getter for the trading interval
    '''

    def getInterval(self):
        return self.interval

    '''
    Getter for the time list
    '''

    def getTime(self):
        return self.time

    '''
    Plots the desired indicator with strategy buy and sell points
    '''

    def plotIndicator(self):
        if self.indicator == 'MACD':
            open_time = [int(entry[0]) for entry in klines]
            new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
            plt.style.use('dark_background')
            plt.plot(new_time, self.indicator_result[0], label='MACD')
            plt.plot(new_time, self.indicator_result[1], label='MACD Signal')
            plt.plot(new_time, self.indicator_result[2], label='MACD Histogram')
            for entry in self.strategy_result:
                plt.plot(entry[0], entry[1], entry[2])
            title = "MACD Plot for " + self.pair + " on " + self.interval
            plt.title(title)
            plt.xlabel("Open Time")
            plt.ylabel("Value")
            plt.legend()
            plt.show()

        else:
            pass


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
            if time[i] > self.startTime and time[i] < self.endTime:
                if (time[i] == strategy_result[point_finder][0]):
                    if strategy_result[point_finder][3] == 'BUY':
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
                        self.trades.append([strategy_result[point_finder][0],'SELL', float(strategy_result[point_finder][4])])
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
            print(entry[1] + " at " + str(entry[2]) + " when " + str(entry[0]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', required=True)
    parser.add_argument('--interval', type=str, help='interval', default="1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M")
    option = parser.parse_args()

    trader = Trader()
    symbol = option.symbol
    interval = option.interval
    intervals = interval.split(",")
    macd_backtests = []
    for interval in intervals:
        klines = trader.client.get_klines(symbol=symbol, interval=interval)
        macd_strategy = Strategy('MACD', 'CROSS', symbol, interval, klines)
        # macd_strategy.plotIndicator()
        time = macd_strategy.getTime()
        macd_backtest = Backtest(10000, time[0], time[len(time) - 1], macd_strategy)
        macd_backtests.append(macd_backtest)
    macd_backtests = sorted(macd_backtests, key=lambda x: x.amount)
    for macd_backtest in macd_backtests[-3:]:
        if macd_backtest.num_trades > 0:
            macd_backtest.printResults()
