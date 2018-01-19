import datetime
import time

import poloniex
from poloniex import PoloniexError

import settings
import util
from AutoTrader.adapter import Market_Adapter

FEE = 0.0025
log = util.setup_logger(__name__)

class Poloniex_Adapter(Market_Adapter):

    def __init__(self, mode="BTC"):
        Market_Adapter.__init__(self, mode)
        auth = util.get_poloniex_auth()
        self.client = poloniex.Poloniex(**auth)
        # timeout for buy, sell orders
        self.timeout = 90
        self.retries = 5
        self.coin_name_array = util.read_subs_from_file(settings.general["poloniex_file"])

    #--------- Buy Operations ---------
    def buy_by_symbol(self, symbol, total):
        if self.mode == "BTC":
            try:
                if self.__buy_with_BTC__(symbol, total):
                    return True
                for _ in range(self.retries):
                    if self.__buy_with_BTC_aggressive__(symbol, total):
                        return True
                log.warn("Reached maximum number of retries for buying %s. Giving up..." %(symbol))
                return False
            except Exception as e:
                log.warn("Could not buy %s. Reason: %s" %(symbol, str(e)))
                return False

    def __buy_with_BTC_aggressive__(self, symbol, total):
        """
        Will buy the coin using BTC for the lowest asking price.
        """
        pair = "BTC_{}".format(symbol)
        rate = self.get_lowest_ask(symbol)
        total = min(total, self.get_portfolio()["BTC"])
        amount = total / ((1. + FEE) * rate)
        # amount = total / rate
        try:
            self.client.buy(pair, rate, amount, 'fillOrKill')
        except PoloniexError as e:
            log.warn("Aggressive buy failed. Could not buy %s for %sBTC. Reason: %s" %(symbol, total, str(e)))
            return False
        log.info("Bought %s %s for %s%s. (aggressive)" %(amount, symbol, total, self.mode))
        return True

    def __buy_with_BTC__(self, symbol, total):
        pair = "BTC_{}".format(symbol)
        rate = self.get_bid_ask_mean(symbol)
        total = min(total, self.get_portfolio()["BTC"])
        amount = total / ((1 + FEE) * rate)
        try:
            order = self.client.buy(pair, rate, amount)
        except PoloniexError as e:
            log.warn("Could not create buy order for %s for %sBTC. Reason: %s" %(symbol, total, str(e)))
            return
        order_nr = order["orderNumber"]
        slept = 0
        while slept < self.timeout:
            completed = True
            open_orders = self.client.returnOpenOrders(pair)
            for o in open_orders:
                if o["orderNumber"] == order_nr:
                    completed = False
                    break
            if completed:
                break
            slept += 5
            time.sleep(5)
        if completed:
            log.info("Bought %s %s for %s%s." %(amount, symbol, total, self.mode))
        else:
            self.client.cancelOrder(order_nr)
        return completed

    #--------- Sell Operations ---------

    def sell_by_symbol(self, symbol, amount):
        """
        Sells the specified coin.
        """
        if (self.mode == "BTC"):
            try:
                if self.__sell_for_BTC__(symbol, amount):
                    return True
                for _ in range(self.retries):
                    if self.__sell_for_BTC_aggressive__(symbol, amount):
                        return True
                log.warn("Reached maximum number of retries for selling %s. Giving up..." %(symbol))
                return False
            except Exception as e:
                log.warn("Could not sell %s. Reason: %s" %(symbol, str(e)))
                return False

    def __sell_for_BTC_aggressive__(self, symbol, amount):
        pair = "BTC_{}".format(symbol)
        rate = self.get_highest_bid(symbol)
        try:
            self.client.sell(pair, rate, amount, 'fillOrKill')
        except PoloniexError as e:
            log.warn("Aggressive sell failed. Could not sell %s %s. Reason: %s" %(amount, symbol, str(e)))
            return False
        log.info("Sold %s %s for %s%s. (aggressive)" %(amount, symbol, rate*amount, self.mode))
        return True

    def __sell_for_BTC__(self, symbol, amount):
        pair = "BTC_{}".format(symbol)
        rate = self.get_bid_ask_mean(symbol)
        try:
            order = self.client.sell(pair, rate, amount)
        except PoloniexError as e:
            log.warn("Could not create sell order for %s %s. Reason: %s" %(amount, symbol, str(e)))
            return
        order_nr = order["orderNumber"]
        slept = 0
        while slept < self.timeout:
            completed = True
            open_orders = self.client.returnOpenOrders(pair)
            for o in open_orders:
                if o["orderNumber"] == order_nr:
                    completed = False
                    break
            if completed:
                break
            slept += 5
            time.sleep(5)
        if completed:
            log.info("Sold %s %s for %s%s." %(amount, symbol, rate*amount, self.mode))
        else:
            self.client.cancelOrder(order_nr)
        return completed

    #--------- Get Operations ---------

    def get_funds(self):
        return self.get_portfolio()[self.mode]

    def get_portfolio(self):
        """
        Returns all non-zero entries of the portfolio.
        """
        portfolio = {}
        balances = self.client.returnBalances()
        for coin in balances:
            if float(balances[coin]) > 0.0:
                portfolio[coin] = float(balances[coin])
        return portfolio

    def get_portfolio_funds_value(self):
        if self.mode == "BTC":
            return self.__get_portfolio_btc_value__()

    def __get_portfolio_btc_value__(self):
        """
        Returns all non-zero entries of the portfolio with the corresponding btc values.
        """
        portfolio = {}
        balances = self.client.returnCompleteBalances()
        for coin in balances:
            if float(balances[coin]["btcValue"]) > 0.0:
                portfolio[coin] = float(balances[coin]["btcValue"])
        return portfolio

    def get_lowest_ask(self, symbol):
        """
        Returns the current lowset asking price for pair.
        """
        pair = "{}_{}".format(self.mode, symbol)
        return float(self.client.returnTicker()[pair]["lowestAsk"])

    def get_highest_bid(self, symbol):
        """
        Returns the highest bid for pair.
        """
        pair = "{}_{}".format(self.mode, symbol)
        return float(self.client.returnTicker()[pair]["highestBid"])

    def get_bid_ask_mean(self, symbol):
        """
        Returns the mean of highest bid and lowest asking price for pair.
        """
        pair = "{}_{}".format(self.mode, symbol)
        ticker = self.client.returnTicker()
        return (float(ticker[pair]["highestBid"]) + float(ticker[pair]["lowestAsk"])) / 2.

    def get_last_trade_date(self):
        """
        Returns the date of the last trade.
        """
        last_week = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        trades = self.client.returnTradeHistory(start=last_week.timestamp())
        dates = []
        for _, trade in trades.items():
            trade_date = datetime.datetime.strptime(trade[0]["date"], '%Y-%m-%d %H:%M:%S')
            dates.append(trade_date)
        if len(dates) == 0:
            return last_week
        return max(dates)

    def get_last_buy_date(self, symbol):
        """
        Returns the date of the last trade.
        """
        pair = "{}_{}".format(self.mode, symbol)
        last_week = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        trades = self.client.returnTradeHistory(currencyPair=pair,start=last_week.timestamp())
        dates = []
        for trade in trades:
            if trade["type"] == "buy":
                trade_date = datetime.datetime.strptime(trade["date"], '%Y-%m-%d %H:%M:%S')
                dates.append(trade_date)
        if len(dates) == 0:
            return last_week
        return max(dates)

    def get_net_worth(self):
        if mode == "BTC":
            self.__get_net_worth_btc__()

    def __get_net_worth_btc__(self):
        balances = self.client.returnCompleteBalances()
        return sum([float(b["btcValue"]) for b in balances.values()])

    def get_min_spend(self):
        """
        Minimum amount needed to spend on this exchange.
        """
        return 0.0001

    def can_sell(self, symbol):
        return self.__get_portfolio_btc_value__()[symbol] > (1 + FEE) * self.get_min_spend()
