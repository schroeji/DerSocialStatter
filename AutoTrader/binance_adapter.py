from binance.client import Client
from AutoTrader.adapter import Market_Adapter
import util

class Binance_Adapter(Market_Adapter):
    def __init__(self):
        auth = util.get_binance_auth()
        self.client = Client(**auth)

    def get_bid_ask_mean(self, symbol):
        pair = "{}BTC".format(symbol)
        ticker = self.client.get_orderbook_ticker(symbol=pair)
        return (float(ticker[pair]["bidPrice"]) + float(ticker[pair]["askPrice"])) / 2.

    def get_highest_bid(self, symbol):
        pair = "{}BTC".format(symbol)
        ticker = self.client.get_orderbook_ticker(symbol=pair)
        return ticker["bidPrice"]

    def get_lowest_ask(self, symbol):
        pair = "{}BTC".format(symbol)
        ticker = self.client.get_orderbook_ticker(symbol=pair)
        return ticker["askPrice"]

    def get_portfolio_btc_value(self):
        """
        Returns all non-zero entries of the portfolio with the corresponding btc values.
        """
        portfolio = {}
        balances = self.get_portfolio()
        tickers = self.client.get_all_tickers()
        for coin, amount in balances.items():
            pair = "{}BTC".format(coin)
            for ticker in tickers:
                if ticker["symbol"] == pair:
                    portfolio[coin] = amount * float(ticker["price"])
        return portfolio

    def get_portfolio(self):
        """
        Returns all non-zero entries of the portfolio.
        """
        balances = self.client.get_account()["balances"]
        portfolio = {}
        for entry in balances:
            if float(entry["free"]) > 0.0:
                portfolio[entry["asset"]] = float(entry["free"])
        return portfolio