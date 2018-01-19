import util
from AutoTrader import (binance_adapter, bittrex_adapter, policies,
                        poloniex_adapter)
from coinmarketcap import CoinCap

log = util.setup_logger(__name__)

class AutoTrader():
    def __init__(self, exchange):
        if exchange.lower() == "poloniex":
            self.adapter = poloniex_adapter.Poloniex_Adapter()
        elif exchange.lower() == "bittrex":
            self.adapter = bittrex_adapter.Bittrex_Adapter()
        elif exchange.lower() == "binance":
            self.adapter = binance_adapter.Binance_Adapter()
        else:
            log.warn("Invalid exchange: {}.".format(exchange))
            raise ValueError("Invalid exchange: {}".format(exchange))

    def run(self):
        portfolio = self.adapter.get_portfolio()
        log.info("Owned coins:")
        util.print_price_dict(portfolio, "%-4s %12f")
        log.info("Owned coins %s value:" % (self.adapter.mode))
        util.print_price_dict(self.adapter.get_portfolio_funds_value(), "%-4s %12f{}".format(self.adapter.mode))
        cap = CoinCap()
        usd_portfolio = cap.get_coin_values_usd(self.adapter.coin_name_array, portfolio)
        log.info("Owned coins USD value:")
        util.print_price_dict(usd_portfolio, "%-4s %.2f$")
        policies.subreddit_growth_policy(self.adapter)
        log.info("Finished trading.")
