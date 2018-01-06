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
        log.info("Owned coins btc value:")
        log.info(self.adapter.get_portfolio_btc_value())
        policies.subreddit_growth_policy(self.adapter)
