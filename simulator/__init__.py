import datetime

import database
import simulator.policies
import util
from simulator.market import Market, Trader

log = util.setup_logger(__name__)

class Simulator(object):
    def __init__(self, trader, start_time, end_time = datetime.datetime.utcnow(),
               market=None, verbose=True):
        if market is None:
            self.market = Market()
        else:
            self.market = market
        self.trader = trader
        self.start_time = start_time
        self.end_time = end_time
        self.time = start_time
        self.verbose = verbose

    def simulation_step(self):
        if self.verbose:
            port_val = self.market.portfolio_value()
            log.info("Time: {}".format(self.time))
            log.info("Coin value: {:8.2f}".format(port_val))
            log.info("funds: {:13.2f}".format(self.trader.funds))
            log.info("Sum: {:15.2f}".format(self.trader.funds + port_val))
        time_delta = self.trader.policy(self.trader, self.time, self.steps)
        self.time += time_delta
        self.steps += 1

    def run(self):
        log.info("Running simulator...")
        self.steps = 0
        while self.time < self.end_time:
            self.simulation_step()
        self.market.sell_all()
        log.info("Simulation finished:")
        log.info("Ran {} steps from {} to {}.".format(self.steps, self.start_time, self.time))
        log.info("Trader finished with {:8.2f}.".format(self.trader.funds))

def simulate(policy):
    """
    Function which sets up and runs the simulator.
    """
    start_time = datetime.datetime.utcnow() - datetime.timedelta(2)
    start_funds = 100.
    auth = util.get_postgres_auth()
    db = database.DatabaseConnection(**auth)
    market = Market(db)
    trader = Trader(db, start_funds, market)
    trader.policy = policy
    sim = Simulator(trader, start_time, market=market)
    market.setSimulator(sim)
    market.setTrader(trader)
    sim.run()
