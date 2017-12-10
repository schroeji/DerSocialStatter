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