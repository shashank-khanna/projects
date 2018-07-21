import logging

import datetime
import numpy as np
import scipy.stats as stats

from option_pricing.base_option_pricing import OptionPricingBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)


class EuropeanOptionPricing(OptionPricingBase):

    def __init__(self, ticker, expiry_date, strike, dividend=0.0):
        super(EuropeanOptionPricing, self).__init__(ticker, expiry_date, strike, dividend=dividend)
        logging.info("European Option Pricing. Initializing variables")
        self.initialize_variables()
        self.log_parameters()

    def _calculate_d1(self):
        d1 = (np.log(self.spot_price / self.strike_price) +
              (self.risk_free_rate - self.dividend + 0.5 * self.volatility ** 2) * self.time_to_maturity) / \
             (self.volatility * np.sqrt(self.time_to_maturity))
        logging.debug("Calculated value for d1 = %f" % d1)
        return d1

    def _calculate_d2(self):
        d2 = (np.log(self.spot_price / self.strike_price) +
              (self.risk_free_rate - self.dividend - 0.5 * self.volatility ** 2) * self.time_to_maturity) / \
             (self.volatility * np.sqrt(self.time_to_maturity))
        logging.debug("Calculated value for d2 = %f" % d2)
        return d2

    def calculate_call_option_price(self):
        d1 = self._calculate_d1()
        d2 = self._calculate_d2()
        call = ((self.spot_price * np.exp(-1 * self.dividend * self.time_to_maturity)) * stats.norm.cdf(d1, 0.0, 1.0) -
                (self.strike_price * np.exp(-1 * self.risk_free_rate * self.time_to_maturity) *
                 stats.norm.cdf(d2, 0.0, 1.0)))
        logging.info("##### Calculated value for European Call Option is %f " % call)
        return call

    def calculate_put_option_price(self):
        d1 = self._calculate_d1()
        d2 = self._calculate_d2()
        put = (self.strike_price * np.exp(-1 * self.risk_free_rate * self.time_to_maturity) *
               stats.norm.cdf(-1 * d2, 0.0, 1.0) - (
                       self.spot_price * np.exp(-1 * self.dividend * self.time_to_maturity)) *
               stats.norm.cdf(-1 * d1, 0.0, 1.0))
        logging.info("##### Calculated value for European Put Option is %f " % put)
        return put


if __name__ == '__main__':
    # pricer = EuropeanOptionPricing('AAPL', datetime.datetime(2020, 6, 19), 190, dividend=0.0157)
    pricer = EuropeanOptionPricing('TSLA', datetime.datetime(2018, 8, 31), 300)
    call_price = pricer.calculate_call_option_price()
    put_price = pricer.calculate_put_option_price()
