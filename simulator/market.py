import database
import settings
import util

log = util.setup_logger(__name__)

class InsufficientFundsException(Exception):

    def __init__(self, coin_name):
        super(InsufficientFundsException, self).__init__("Trader does not have enough {}.".format(coin_name))

class Trader(object):
    """
    Generic class which can be extended to implement traders.
    """

    def __init__(self, db, start_funds, market):
        """
        Constructor for star funds in USD and a market object.
        """
        self.funds = start_funds
        self.market = market
        self.db = db

    def policy(self, time, step_nr):
        pass

class Market(object):
    """
    A class which can simulate the interaction with a market for a trader.
    """

    def __init__(self, db, simulator=None, coins=None, fees=0, verbose=True):
        if coins is None:
            coins = util.read_csv(settings.general["subreddit_file"])
        self.fees = fees
        self.portfolio = {}
        for coin in coins:
            self.portfolio[coin[-1]] = 0.0
        self.db = db
        self.simulator = simulator
        self.verbose = verbose
        self.transaction_log = {}

    def setSimulator(self, sim):
        self.simulator = sim

    def buy(self, trader, coin, total):
        """
        Allows a trader to buy coins in this market.
        If he has enough funds.
        """
        if (trader.funds < total or total == 0.0):
            raise InsufficientFundsException("FUNDS")
        current_price = self.db.get_interpolated_price_data(coin, self.simulator.time)[0]
        trader.funds -= total
        bought_coins = total * (1-self.fees) / current_price
        self.portfolio[coin] += bought_coins
        if self.verbose:
            log.info("Bought {:8.4f} {} for {:5.2f}.".format(bought_coins, coin, total))

    def sell(self, trader, coin, total=None):
        """
        Allows a trader to sell coins in this market.
        If total is not given all coins of the given type will be sold.
        """
        if total is None:
            total = self.portfolio[coin]
        if self.portfolio[coin] < total or total == 0:
            raise InsufficientFundsException(coin)
        current_value = self.db.get_interpolated_price_data(coin, self.simulator.time)[0]
        dollars = (1-self.fees) * total * current_value
        trader.funds += dollars
        if self.verbose:
            log.info("Sold {:8.4f} {} for ${:5.2f}.".format(total, coin, dollars))

    def owned_coins(self):
        """
        Returns a dict with the owned coins and current balance if the current balance is > 0.
        """
        ret_dict = {}
        for k, d in self.portfolio.items():
            if d > 0:
                ret_dict[k] = d
        return ret_dict

    def current_balance(self, coin):
        return self.portfolio[coin]

    def sell_all(self, trader):
        """
        Will sell all coins the trader owns.
        """
        for coin, balance in self.portfolio.items():
            if balance > 0:
                self.sell(trader, coin)

    def portfolio_value(self, trader):
        """
        Returns the current total value of the portfolio.
        """
        total_value = 0.0
        for coin, balance in self.portfolio.items():
            if balance > 0:
                current_value = self.db.get_interpolated_price_data(coin, self.simulator.time)[0]
                total_value += current_value * balance
        return total_value
