import util
class Market_Adapter(object):

    def __init__(self):
        self.coin_name_array = []

    #--------- Buy Operations ---------
    def buy_by_sub(self, sub, amount):
        symbol = util.get_symbol_for_sub(self.coin_name_array, sub)
        self.buy_by_symbol(symbol, amount)

    def buy_by_symbol(self, symbol, total):
        pass
    #--------- Sell Operations ---------

    def sell_by_sub(self, sub, amount):
        symbol = util.get_symbol_for_sub(self.coin_name_array, sub)
        self.sell_by_symbol(symbol, amount)

    def sell_by_symbol(self, symbol, amount):
        """
        Sells the specified coin.
        """
        pass

    def sell_all(self, symbol):
        """
        Sell all of the speciefied coin.
        """
        amount = self.get_portfolio()[symbol]
        self.sell_by_symbol(symbol, amount)

    def sell_all_coins(self):
        portfolio = self.get_portfolio()
        for coin in portfolio:
            if coin == "BTC":
                continue
            self.sell_by_symbol(coin, portfolio[coin])

    #--------- Get Operations ---------

    def get_btc(self):
        pass

    def get_portfolio(self):
        """
        Returns all non-zero entries of the portfolio.
        """
        pass

    def get_portfolio_btc_value(self):
        """
        Returns all non-zero entries of the portfolio with the corresponding btc values.
        """
        pass

    def get_lowest_ask(self, pair):
        """
        Returns the current lowset asking price for pair.
        """
        pass

    def get_highest_bid(self, pair):
        """
        Returns the highest bid for pair.
        """
        pass

    def get_bid_ask_mean(self, pair):
        """
        Returns the mean of highest bid and lowest asking price for pair.
        """
        pass

    def get_last_trade_date(self):
        """
        Returns the date of the last trade
        """
        pass

    def get_coins(self):
        return self.coin_name_array

    def get_net_worth(self):
        """
        SUm of the btc value of all coins.
        """
        pass

    def get_min_spend(self):
        """
        Minimum amount needed to spend on this exchange.
        """
        return 0