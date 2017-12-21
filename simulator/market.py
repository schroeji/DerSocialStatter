from .. import util
from .. import settings
from .. import database
import datetime

class InsufficientFundsException(Exception):
    def __init__(self, coin_name):
        super(InsufficientFundsException, self).__init__("Trader does not have enough {}.".format(coin_name))

class Trader(object):

    def __init__(self, start_time, start_funds, market, time_delta=datetime.timedelta(1)):
        self.time = start_time
        self.funds = start_funds
        self.time_delta = time_delta

    def timestep(self):
        self.time += self.time_delta

    def policy(self):
        pass

class Market(object):
    """
    A class which can simulate the interaction with a market for a trader.
    """

    def __init__(self, coins=None, fees=0):
        if coins is None:
            coins = util.read_csv(settings.general.subreddit_file)
        self.fees = fees
        self.portfolio = {}
        for coin in coins:
            self.portfolio[coin] = 0.0
        self.db = database.DatabaseConnection()

    def buy(self, trader, coin, total):
        """
        Allows a trader to buy coins in this market.
        If he has enough funds.
        """
        if (trader.funds < total):
            raise InsufficientFundsException("FUNDS")
        current_price = self.db.get_interpolated_price_data(coin[-1], trader.time)[0]
        trader.funds -= total
        self.portfolio[coin] += total * (1-self.fees) * current_price

    def sell(self, trader, coin, total=None):
        """
        Allows a trader to sell coins in this market.
        If total is not given all coins of the given type will be sold.
        """
        if total is None:
            total = self.portfolio[coin]
        if self.portfolio[coin] < total or total == 0:
            raise InsufficientFundsException(coin[0])
        current_value = self.db.get_interpolated_price_data(coin[-1], trader.time)[0]
        trader.funds += (1-self.fees) * total * current_value

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