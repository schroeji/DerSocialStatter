import requests
import json

class CoinCap(object):
    """
    A class which manages connections to the CoinMarketCap.com API
    """
    def __init__(self):
        self.url = "https://api.coinmarketcap.com/v1/ticker/"

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

    def get_coin_price_data(self, coin_names):
        """
        get the price data for all coin in coins
        """
        json_url = "{}?limit={}".format(self.url, 300)
        resp = requests.get(url=json_url)
        data = json.loads(resp.text)
        d = {}
        for coin in data:
            normalized_id = "".join(x for x in coin["id"] if x.isalnum())
            if normalized_id in coin_names or coin["id"] in coin_names or coin["name"] in coin_names:
                d[normalized_id] = {
                    "coin_id" : coin["id"],
                    "coin_name" : coin["name"],
                    "symbol" : coin["symbol"],
                    "percent_change_1h" : coin["percent_change_1h"],
                    "percent_change_24h" : coin["percent_change_24h"],
                    "price" : coin["price_usd"],
                }
        return d