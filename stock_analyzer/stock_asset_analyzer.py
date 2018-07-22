import logging

import matplotlib.pyplot as plt
from matplotlib import style

from stock_analyzer.analyzer_base import AnalyzerBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)

style.use('ggplot')


class StockAssetAnalyzer(AnalyzerBase):

    def __init__(self, ticker):
        super(StockAssetAnalyzer, self).__init__(ticker)
        # Get underlying data and setup required parameters
        self.setup_underlying_data()

    @property
    def asset_returns(self):
        if self.stock_data.empty:
            raise ValueError("Historical stock prices unavailable")
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
    analyzer.plot_returns()
    analyzer.plot_returns_against_snp500()
    print("Alpha ", analyzer.alpha)
    print("Beta ", analyzer.beta)
    print(analyzer.ols_model.summary())
