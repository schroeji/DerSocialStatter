import poloniex
from poloniex import PoloniexError
import time
import datetime

import util
import settings

log = util.setup_logger(__name__)

class Poloniex_Adapter:

    def __init__(self):
        auth = util.get_poloniex_auth()
        self.polo = poloniex.Poloniex(**auth)
        # timeout for buy, sell orders
        self.timeout = 90
        self.retries = 5
        self.coin_name_array = util.read_subs_from_file(settings.general["poloniex_file"])

    def buy_by_sub(self, sub, amount):
        symbol = util.get_symbol_for_sub(self.coin_name_array, sub)
        self.buy_by_symbol(symbol, amount)

    def buy_by_symbol(self, symbol, total):
        if self.__buy_with_BTC__(symbol, total):
            return True
        for _ in range(self.retries):
            if self.__buy_with_BTC_aggressive__(symbol, total):
                return True
        log.warn("Reached maximum number of retries for buying %s. Giving up..." %(symbol))
        return False

    def sell_by_sub(self, sub, amount):
        symbol = util.get_symbol_for_sub(self.coin_name_array, sub)
        self.sell_by_symbol(symbol, amount)

    def sell_by_symbol(self, symbol, amount):
        if self.__sell_for_BTC__(symbol, amount):
            return True
        for _ in range(self.retries):
            if self.__sell_for_BTC_aggressive__(symbol, amount):
                return True
        log.warn("Reached maximum number of retries for selling %s. Giving up..." %(symbol))
        return False

    def __buy_with_BTC_aggressive__(self, symbol, total):
        """
        Will buy the coin using BTC for the lowest asking price.
        """
        pair = "BTC_{}".format(symbol)
        rate = self.get_lowest_ask(pair)
        # amount = total / ((1. + FEE) * rate)
        amount = total / rate
        try:
            self.polo.buy(pair, rate, amount, 'fillOrKill')
        except PoloniexError as e:
            log.warn("Aggressive buy failed. Could not buy %s for %sBTC. Reason: %s" %(amount, symbol, str(e)))
            return False
        return True

    def __buy_with_BTC__(self, symbol, total):
        pair = "BTC_{}".format(symbol)
        rate = self.get_bid_ask_mean(pair)
        amount = total / rate
        try:
            order = self.polo.buy(pair, rate, amount)
        except PoloniexError as e:
            log.warn("Could not create buy order %s for %sBTC. Reason: %s" %(amount, symbol, str(e)))
            return
        order_nr = order["orderNumber"]
        slept = 0
        while slept < self.timeout:
            completed = True
            open_orders = self.polo.returnOpenOrders(pair)
            for o in open_orders:
                if o["orderNumber"] == order_nr:
                    completed = False
                    break
            if completed:
                break
            slept += 5
            time.sleep(5)
        if completed:
            log.info("Bought %s %s at %s." %(amount, symbol, rate))
        else:
            self.polo.cancelOrder(order_nr)
        return completed

    def __sell_for_BTC_aggressive__(self, symbol, amount):
        pair = "BTC_{}".format(symbol)
        rate = self.get_highest_bid(pair)
        try:
            self.polo.sell(pair, rate, amount, 'fillOrKill')
        except PoloniexError as e:
            log.warn("Aggressive sell failed. Could not sell %s %s. Reason: %s" %(amount, symbol, str(e)))
            return False
        return True

    def __sell_for_BTC__(self, symbol, amount):
        pair = "BTC_{}".format(symbol)
        rate = self.get_bid_ask_mean(pair)
        try:
            order = self.polo.sell(pair, rate, amount)
        except PoloniexError as e:
            log.warn("Could not create sell order for %s %s. Reason: %s" %(amount, symbol, str(e)))
            return
        order_nr = order["orderNumber"]
        slept = 0
        while slept < self.timeout:
            completed = True
            open_orders = self.polo.returnOpenOrders(pair)
            for o in open_orders:
                if o["orderNumber"] == order_nr:
                    completed = False
                    break
            if completed:
                break
            slept += 5
            time.sleep(5)
        if completed:
            log.info("Sold %s %s at %s." %(amount, symbol, rate))
        else:
            self.polo.cancelOrder(order_nr)
        return completed

    def sell_all(self, symbol):
        amount = self.get_portfolio()[symbol]
        self.sell_by_symbol(symbol, amount)

    def sell_all_coins(self):
        portfolio = self.get_portfolio()
        print(portfolio)
        for coin in portfolio:
            if coin == "BTC":
                continue
            self.sell_by_symbol(coin, portfolio[coin])

    def get_btc(self):
        return self.get_portfolio()["BTC"]

    def get_portfolio(self):
        """
        Returns all non-zero entries of the portfolio.
        """
        portfolio = {}
        balances = self.polo.returnBalances()
        for coin in balances:
            if float(balances[coin]) > 0.0:
                portfolio[coin] = float(balances[coin])
        return portfolio

    def get_lowest_ask(self, pair):
        """
        Returns the current lowset asking price for pair.
        """
        return float(self.polo.returnTicker()[pair]["lowestAsk"])

    def get_highest_bid(self, pair):
        """
        Returns the highest bid for pair.
        """
        return float(self.polo.returnTicker()[pair]["highestBid"])

    def get_bid_ask_mean(self, pair):
        """
        Returns the mean of highest bid and lowest asking price for pair.
        """
        ticker = self.polo.returnTicker()
        return (float(ticker[pair]["highestBid"]) + float(ticker[pair]["lowestAsk"])) / 2.

    def get_last_trade(self):
        last_week = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        trades = self.polo.returnTradeHistory(start=last_week.timestamp())
        dates = []
        for _, trade in trades.items():
            trade_date = datetime.datetime.strptime(trade[0]["date"], '%Y-%m-%d %H:%M:%S')
            dates.append(trade_date)
        return max(dates)