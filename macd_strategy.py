from datetime import datetime, timedelta, timezone
import logging

import talib as ta
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


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
                new_time = [datetime.fromtimestamp(time / 1000, tz=timezone(timedelta(seconds=8*3600))) for time in open_time]
                self.time = new_time
                crosses = []
                macdabove = False
                # Runs through each timestamp in order
                for i in range(len(self.indicator_result[0])):
                    if np.isnan(self.indicator_result[0][i]) or np.isnan(self.indicator_result[1][i]):
                        pass
                    # If both the MACD and signal are well defined, we compare the 2 and decide if a cross has occured
                    else:
                        if i >= 5:
                            for j in range(i-5, i+1):
                                if np.isnan(self.indicator_result[0][j]) or np.isnan(self.indicator_result[1][j]):
                                    break
                                assert self.indicator_result[0][j] - self.indicator_result[1][j] == self.indicator_result[2][j]
                            else:
                                std = np.std([self.indicator_result[2][j] for j in range(i-5, i+1)], ddof=1)
                                if std < 0.01:
                                    # logger.info("%r std:%s time:%s", [self.indicator_result[2][j] for j in range(i-5, i+1)], std, new_time[i])
                                    continue
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
            open_time = [int(entry[0]) for entry in self.klines]
            new_time = [datetime.fromtimestamp(time / 1000, tz=timezone(timedelta(seconds=8*3600))) for time in open_time]
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
            plt.savefig("images/" + title.replace(" ", "_") + ".png")
            plt.clf()

        else:
            pass
