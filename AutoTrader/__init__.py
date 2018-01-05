from AutoTrader.poloniex_adapter import Poloniex_Adapter
from AutoTrader.bittrex_adapter import Bittrex_Adapter
from AutoTrader import policies
import util

log = util.setup_logger(__name__)

class AutoTrader():
    def __init__(self, market):
        if market == "Poloniex":
            self.adapter = Poloniex_Adapter()
        elif market == "Bittrex":
            self.adapter = Bittrex_Adapter()
        else:
            log.warn("Invalid market {}.".format(market))

    def run(self):
        for _ in range(20):
            self.adapter.get_lowest_ask("DGB")
        # policies.subreddit_growth_policy(self.adapter)