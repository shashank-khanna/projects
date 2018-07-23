import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay

from stock_analyzer.stock_asset_analyzer import StockAssetAnalyzer


class BackTestingBase(object):
    INITIAL_CAPITAL = float(100000.0)

    def __init__(self, ticker, look_back_days=None):
        self.ticker = ticker
        self.stock_data = pd.DataFrame()
        self.asset_analyzer = None
        self.signals = pd.DataFrame()
        self.portfolio = None
        self.get_underlying_data(look_back_days)

    def get_underlying_data(self, look_back_days=None):
        if look_back_days:
            start_date = datetime.datetime.today() - BDay(look_back_days)
            self.asset_analyzer = StockAssetAnalyzer(self.ticker, hist_start_date=start_date, refresh=True)
        else:
            self.asset_analyzer = StockAssetAnalyzer(self.ticker, datetime.datetime.today() - BDay(2000))
        self.stock_data = self.asset_analyzer.stock_data

    def backtest(self):
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        positions[self.ticker] = 100 * self.signals['signal']
        # Initialize the portfolio with value owned
        self.portfolio = positions.multiply(self.stock_data['Close'], axis=0)

        # Store the difference in shares owned
        pos_diff = positions.diff()

        # Add `holdings` to portfolio
        self.portfolio['holdings'] = (positions.multiply(self.stock_data['Close'], axis=0)).sum(axis=1)

        # Add `cash` to portfolio
        self.portfolio['cash'] = self.INITIAL_CAPITAL - \
                                 (pos_diff.multiply(self.stock_data['Close'], axis=0)).sum(axis=1).cumsum()

        # Add `total` to portfolio
        self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdings']

        # Add `returns` to portfolio
        self.portfolio['returns'] = self.portfolio['total'].pct_change()

        # Print the first lines of `portfolio`
        print(self.portfolio.head())

    def plot_portfolio(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')
        ax1.plot(self.signals.index.map(mdates.date2num), self.portfolio['total'])
        ax1.plot(self.portfolio.loc[self.signals.positions == 1.0].index,
                 self.portfolio.total[self.signals.positions == 1.0],
                 '^', markersize=10, color='m')
        ax1.plot(self.portfolio.loc[self.signals.positions == -1.0].index,
                 self.portfolio.total[self.signals.positions == -1.0],
                 'v', markersize=10, color='k')
        plt.show()

    def sharpe_ratio(self):
        # Isolate the returns of your strategy
        returns = self.portfolio['returns']

        # annualized Sharpe ratio
        sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())

        # Print the Sharpe ratio
        print("Sharpe Ratio", sharpe_ratio)
        return sharpe_ratio
