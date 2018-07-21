import logging
from random import gauss

import datetime
import numpy as np

from option_pricing.base_option_pricing import OptionPricingBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)


class AmericanOptionPricing(OptionPricingBase):
    SIMULATION_COUNT = 100000

    def __init__(self, ticker, expiry_date, strike, dividend=0.0):
        super(AmericanOptionPricing, self).__init__(ticker, expiry_date, strike, dividend=dividend)
        logging.info("American Option Pricing. Initializing variables")
        self.initialize_variables()
        self.log_parameters()

    def _generate_asset_price(self):
        expected_price = self.spot_price * np.exp(
            (self.risk_free_rate - 0.5 * self.volatility ** 2) * self.time_to_maturity +
            self.volatility * np.sqrt(self.time_to_maturity) * gauss(0.0, 1.0))
        # logging.debug("expected price %f " % expected_price)
        return expected_price

    def _call_payoff(self, expected_price):
        return max(0, expected_price - self.strike_price)

    def _put_payoff(self, expected_price):
        return max(0, self.strike_price - expected_price)

    def _generate_simulations(self):
        call_payoffs, put_payoffs = [], []
        for _ in xrange(self.SIMULATION_COUNT):
            expected_asset_price = self._generate_asset_price()
            call_payoffs.append(self._call_payoff(expected_asset_price))
            put_payoffs.append(self._put_payoff(expected_asset_price))
        return call_payoffs, put_payoffs

    def calculate_option_prices(self):
        call_payoffs, put_payoffs = self._generate_simulations()
        discount_factor = np.exp(-1 * self.risk_free_rate * self.time_to_maturity)
        call_price = discount_factor * (sum(call_payoffs) / len(call_payoffs))
        put_price = discount_factor * (sum(put_payoffs) / len(put_payoffs))
        logging.info("### Call Price calculated at %f " % call_price)
        logging.info("### Put Price calculated at %f " % put_price)
        return call_price, put_price

    def is_call_put_parity_maintained(self, call_price, put_price):
        lhs = call_price - put_price
        rhs = self.spot_price - np.exp(-1 * self.risk_free_rate * self.time_to_maturity) * self.strike_price
        logging.info("Put-Call Parity LHS = %f" % lhs)
        logging.info("Put-Call Parity RHS = %f" % rhs)
        return bool(round(lhs) == round(rhs))


if __name__ == '__main__':
    # pricer = AmericanOptionPricing('AAPL', datetime.datetime(2019, 1, 19), 190, dividend=0.0157)
    pricer = AmericanOptionPricing('TSLA', datetime.datetime(2018, 8, 31), 300)
    call, put = pricer.calculate_option_prices()
    parity = pricer.is_call_put_parity_maintained(call, put)
    print("Parity = %s" % parity)
