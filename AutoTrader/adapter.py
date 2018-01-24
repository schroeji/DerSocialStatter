import util


class Market_Adapter(object):

    def __init__(self, mode):
        if not mode in ["ETH", "BTC"]:
            raise ValueError("Invalid mode")
        self.mode = mode
        self.name = "Generic"
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
            if coin == mode:
                continue
            self.sell_by_symbol(coin, portfolio[coin])

    #--------- Get Operations ---------

    def get_funds(self):
        pass

    def get_portfolio(self):
        """
        Returns all non-zero entries of the portfolio.
        """
        pass

    def get_portfolio_funds_value(self):
        """
        Returns all non-zero entries of the portfolio with the corresponding values in self.mode.
        """
        pass

    def get_lowest_ask(self, symbol):
        """
        Returns the current lowset asking price for symbol.
        """
        pass

    def get_highest_bid(self, symbol):
        """
        Returns the highest bid for symbol.
        """
        pass

    def get_bid_ask_mean(self, symbol):
        """
        Returns the mean of highest bid and lowest asking price for symbol.
        """
        pass

    def get_last_trade_date(self):
        """
        Returns the datetime of the last trade.
        """
        pass

    def get_last_buy_date(self, symbol):
        """
        Returns the datetime of the last buy of symbol.
        """
        pass

    def get_coins(self):
        return self.coin_name_array

    def get_net_worth(self):
        """
        Sum of the self.mode value of all coins.
        """
        pass

    def get_min_spend(self):
        """
        Minimum amount needed to spend on this exchange.
        """
        return 0

    def can_sell(self, symbol):
        """
        Can symbol be sold or are there any market restrictions (i.e. min value).
        """
        return True

    def can_buy(self, symbol, spend_amount):
        """
        Can symbol be sold or are there any market restrictions (i.e. min value).
        """
        return True
