import logging

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import style
from mpl_finance import candlestick_ohlc

from stock_analyzer.analyzer_base import AnalyzerBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)

style.use('ggplot')


class StockAssetAnalyzer(AnalyzerBase):

    def __init__(self, ticker):
        super(StockAssetAnalyzer, self).__init__(ticker)
        # Get underlying data and setup required parameters
        self.setup_underlying_data(refresh=False)

    @property
    def asset_returns(self):
        if self.stock_data.empty:
            raise ValueError("Historical stock prices unavailable")
        print(self.stock_data.head())
        self.stock_data['returns'] = self.stock_data['Close'].pct_change()
        return self.stock_data.returns[1:]

    @property
    def index_returns(self):
        if self.sp500_data.empty:
            raise ValueError("Historical stock prices unavailable")
        self.sp500_data['returns'] = self.sp500_data['Close'].pct_change()
        return self.sp500_data.returns[1:]

    def plot_returns(self):
        plt.figure(figsize=(10, 5))
        self.asset_returns.plot()
        plt.ylabel("Daily Returns of %s " % self.ticker)
        plt.show()

    def plot_returns_against_snp500(self):
        plt.figure(figsize=(10, 5))
        self.asset_returns.plot()
        self.index_returns.plot()
        plt.ylabel("Daily Returns of %s against SNP500" % self.ticker)
        plt.show()

    def plot_candlestick(self):
        df_ohlc = self.stock_data['Close'].resample('4D').ohlc()
        df_volume = self.stock_data['Volume'].resample('4D').sum()
        df_ohlc = df_ohlc.reset_index()
        df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)

        fig = plt.figure(figsize=(20, 10))
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(self.ticker)
        plt.legend()
        plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0.8)

        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
        ax1.xaxis_date()
        # candlestick_ohlc(ax1, df_ohlc.values, width=2, colorup='g')
        candlestick_ohlc(ax1, df_ohlc.values, width=3, colorup='#77d879', colordown='#db3f3f')
        ax2.bar(df_volume.index.map(mdates.date2num), df_volume.values)
        # ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
        plt.show()

    @property
    def alpha(self):
        return self.ols_model.params[0]

    @property
    def beta(self):
        return self.ols_model.params[1]

    @property
    def ols_model(self):
        return AnalyzerBase.ordinary_least_square_model(self.asset_returns, self.index_returns)


if __name__ == '__main__':
    analyzer = StockAssetAnalyzer('TSLA')
    print(analyzer.asset_returns.head())
    print(analyzer.index_returns.head())
    # analyzer.plot_returns()
    # analyzer.plot_returns_against_snp500()
    print("Alpha ", analyzer.alpha)
    print("Beta ", analyzer.beta)
    print(analyzer.ols_model.summary())
    analyzer.plot_candlestick()
    #analyzer.stock_data.Date
