import util
from AutoTrader import (binance_adapter, bittrex_adapter, policies,
                        poloniex_adapter)

log = util.setup_logger(__name__)

class AutoTrader():
    def __init__(self, market):
        if market == "Poloniex":
            self.adapter = poloniex_adapter.Poloniex_Adapter()
        elif market == "Bittrex":
            self.adapter = bittrex_adapter.Bittrex_Adapter()
        elif market == "Binance":
            self.adapter = binance_adapter.Binance_Adapter()
        else:
            log.warn("Invalid market {}.".format(market))

    def run(self):
        log.info("Owned coins:")
        log.info(self.adapter.get_portfolio())
        log.info("Owned coins %s value:" % (self.adapter.mode))
        log.info(self.adapter.get_portfolio_funds_value())
        self.adapter.buy_by_symbol("EOS", 0.001)

        # policies.subreddit_growth_policy(self.adapter)
