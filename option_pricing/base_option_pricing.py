import logging

import datetime
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay

from stock_analyzer.data_fetcher import get_data, get_treasury_rate

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


class OptionPricingBase(object):
    LOOK_BACK_WINDOW = 252

    def __init__(self, ticker, expiry_date, strike, dividend=0.0):
        self.ticker = ticker
        self.expiry = expiry_date
        self.strike_price = strike
        self.volatility = None
        self.time_to_maturity = None
        self.risk_free_rate = None
        self.spot_price = None
        self.dividend = dividend or 0.0
        self.__underlying_asset_data = pd.DataFrame()
        self.__start_date = datetime.datetime.today() - BDay(self.LOOK_BACK_WINDOW)

    def initialize_variables(self):
        logging.debug("initializing variables started")
        self._set_risk_free_rate()
        self._set_time_to_maturity()
        self._set_volatility()
        self._set_spot_price()
        logging.debug("initializing variables completed")

    def _set_risk_free_rate(self):
        logging.info("Fetching Risk Free Rate")
        self.risk_free_rate = get_treasury_rate() / 100.0
        logging.info("Risk Free Rate = %d" % self.risk_free_rate)

    def _set_time_to_maturity(self):
        if self.expiry < datetime.datetime.today():
            logging.error("Expiry/Maturity Date is in the past. Please check...")
            raise ValueError("Expiry/Maturity Date is in the past. Please check...")
        self.time_to_maturity = (self.expiry - datetime.datetime.today()).days / 365.0
        logging.info("Setting Time To Maturity to %d days as Expiry/Maturity Date provided is %s "
                     % (self.time_to_maturity, self.expiry))

    def override_historical_start_date(self, hist_start_date):
        self.__start_date = hist_start_date

    def _get_underlying_asset_data(self):
        if self.__underlying_asset_data.empty:
            logging.debug(
                "Getting historical stock data for %s; used to calculate volatility in this asset" % self.ticker)
            self.__underlying_asset_data = get_data(self.ticker, self.__start_date, None, useQuandl=False)
            if self.__underlying_asset_data.empty:
                logging.error("Unable to get historical stock data")
                raise IOError("Unable to get historical stock data for %s!!" % self.ticker)

    def _set_volatility(self):
        self._get_underlying_asset_data()
        self.__underlying_asset_data.reset_index(inplace=True)
        self.__underlying_asset_data.set_index("Date", inplace=True)
        logging.debug("# now calculating log returns")
        self.__underlying_asset_data['log_returns'] = np.log(
            self.__underlying_asset_data['Close'] / self.__underlying_asset_data['Close'].shift(1))
        logging.debug("# now calculating annualized volatility")
        d_std = np.std(self.__underlying_asset_data.log_returns)
        std = d_std * 252 ** 0.5
        logging.info("# Annualized Volatility calculated is {:f} ".format(std))
        self.volatility = std

    def _set_spot_price(self):
        self._get_underlying_asset_data()
        print(self.__underlying_asset_data['Close'][-1])
        self.spot_price = self.__underlying_asset_data['Close'][-1]

    def log_parameters(self):
        logging.info("### TICKER = %s " % self.ticker)
        logging.info("### STRIKE = %f " % self.strike_price)
        logging.info("### DIVIDEND = %f " % self.dividend)
        logging.info("### VOLATILITY = %f " % self.volatility)
        logging.info("### TIME TO MATURITY = %f " % self.time_to_maturity)
        logging.info("### RISK FREE RATE = %f " % self.risk_free_rate)
        logging.info("### SPOT PRICE = %f " % self.spot_price)


if __name__ == '__main__':
    pricer = OptionPricingBase('AAPL', datetime.datetime(2018, 9, 20), 190)
    pricer.initialize_variables()
    print(pricer.spot_price)
