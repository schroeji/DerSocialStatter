from bittrex.bittrex import Bittrex, API_V2_0
from bittrex.bittrex import *
from AutoTrader.adapter import Market_Adapter
import util

class Bittrex_Adapter(Market_Adapter):
    def __init__(self):
        auth = util.get_bittrex_auth()
        self.bitt = Bittrex(auth["key"], auth["secret"], api_version=API_V2_0)
        self.timeout = 90
        self.retries = 5

    def buy_by_symbol(self, symbol, total):
        pair = "BTC-{}".format(symbol)
        self.bitt.trade_buy(market=pair, order_type="LIMIT")

    def get_btc(self):
        val = self.bitt.get_balance("BTC")["result"]
        if val is None:
            return 0.0
        return val

    def get_highest_bid(self, symbol):
        pair = "BTC-{}".format(symbol)
        ticker = self.bitt.get_orderbook(pair)["result"]["buy"]
        # print(ticker)
        return float(ticker[0]["Rate"])

    def get_lowest_ask(self, symbol):
        pair = "BTC-{}".format(symbol)
        candle = self.bitt.get_latest_candle(pair, TICKINTERVAL_ONEMIN)
        print(candle)
        # print(ticker)
        # return float(ticker[0]["Rate"])