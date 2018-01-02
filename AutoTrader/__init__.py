import poloniex
from poloniex import PoloniexError

import util

FEE = 0.0025
log = util.setup_logger(__name__)

class Poloniex_Adapter:

    def __init__(self):
        auth = util.get_poloniex_auth()
        self.polo = poloniex.Poloniex(**auth)
        # timeout for buy, sell orders
        self.timeout = 120

    def buy_by_symbol(self, symbol, total):
        self.__buy_with_BTC__(symbol, total)

    def sell_by_symbol(self, symbol, total):
        self.__buy_with_BTC__(symbol, total)

    def __buy_with_BTC__(self, symbol, total):
        pair = "BTC_{}".format(symbol)
        rate = self.get_bid_ask_mean(pair)
        amount = total / ((1. + FEE) * rate)
        try:
            # TODO more/less aggressive
            order = self.polo.buy(pair, rate, amount)
        except PoloniexError as e:
            log.warn("Could not buy {} for {}BTC. Reason: {}".format(symbol, total, str(e)))

    def __sell_with_BTC__(self, symbol, amount):
        pair = "BTC_{}".format(symbol)
        rate = self.get_highest_bid(pair)
        try:
            # TODO more/less aggressive
            order = self.polo.sell(pair, rate, amount, 'fillOrKill')
        except PoloniexError as e:
            log.warn("Could not sell {} {}. Reason: {}".format(amount, symbol, str(e)))

    def get_lowest_ask(self, pair):
        return float(self.polo.returnTicker()[pair]["lowestAsk"])

    def get_highest_bid(self, pair):
        return float(self.polo.returnTicker()[pair]["highestBid"])

    def get_bid_ask_mean(self, pair):
        ticker = self.polo.returnTicker()
        return (float(ticker[pair]["highestBid"]) + float(ticker[pair]["lowestAsk"])) / 2.

class AutoTrader():
    def __init__(self, market):
        if market == "Poloniex":
            self.adapter = Poloniex_Adapter()
        else:
            log.warn("Invalid market {}.".format(market))

    def run(self):
        self.adapter.buy_by_symbol("ETH", 0.0002)
