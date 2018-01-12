import util
from AutoTrader import (binance_adapter, bittrex_adapter, policies,
                        poloniex_adapter)

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
        log.info("Owned coins:")
        log.info(self.adapter.get_portfolio())
        log.info("Owned coins %s value:" % (self.adapter.mode))
        log.info(self.adapter.get_portfolio_funds_value())
        policies.subreddit_growth_policy(self.adapter)
        log.info("Finished trading.")
