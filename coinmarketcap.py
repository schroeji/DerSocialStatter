import json

import requests

import util

log = util.setup_logger(__name__)
class CoinCap(object):
    """
    A class which manages connections to the CoinMarketCap.com API
    """
    def __init__(self):
        self.url = "https://api.coinmarketcap.com/v1/ticker/"

    def get_coin_values_usd(self, coin_amount_dict):
        """
        For a dictionary which maps coin to their amount returns a
        dictionary which maps those coints to the corresponding values in USD.
        """
        coin_name_array = list(coin_amount_dict.keys())
        price_data = self.get_coin_price_data(coin_name_array)
        d = {}
        for coin, amount in coin_amount_dict:
            d[coin] = amount * price_data[coin]
        return d

    def get_coin_names(self, count):
        """
        get the top count crypto coins
        """
        json_url = self.url + "?limit={}".format(count)
        resp = requests.get(url=json_url)
        data = json.loads(resp.text)
        return [coin["id"] for coin in data]

    def get_coin_aliases(self, count):
        """
        get the id, name, and symbol of the top count crypto coins
        """
        json_url = "{}?limit={}".format(self.url, count)
        resp = requests.get(url=json_url)
        data = json.loads(resp.text)
        return [ [coin["id"], coin["name"], coin["symbol"]] for coin in data]

    def get_coin_price_data(self, coin_name_array):
        """
        get the price data for all coins in coin_name_array
        """
        json_url = "{}?limit={}".format(self.url, 1000)
        resp = requests.get(url=json_url)
        data = json.loads(resp.text)
        d = {}
        for coin in coin_name_array:
            matched = False
            for api_coin in data:
                normalized_id = "".join(x for x in api_coin["id"] if x.isalnum()).lower()
                if (normalized_id in coin) or (api_coin["id"] in coin) or \
                   (api_coin["name"] in coin) or (api_coin["symbol"] in coin):
                    d[normalized_id] = {
                        "coin_id" : api_coin["id"],
                        "coin_name" : api_coin["name"],
                        "symbol" : api_coin["symbol"],
                        "percent_change_1h" : api_coin["percent_change_1h"],
                        "percent_change_24h" : api_coin["percent_change_24h"],
                        "price" : api_coin["price_usd"],
                    }
                    matched = True
                    break
            if not matched:
                log.warning("No match for {}".format(coin[0]))
        return d
