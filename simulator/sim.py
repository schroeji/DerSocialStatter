import datetime

from market import Market, Trader
from util import setup_logger

log = setup_logger(__name__)

class Simulator(object):
    def __init__(self, trader, start_time, end_time = datetime.datetime.utcnow(),
               time_delta = datetime.timedelta(hours=1), market=None):
        if market is None:
            self.market = Market()
        else:
            self.market = market
        self.trader = trader
        self.time_delta = time_delta
        self.start_time = start_time
        self.time = start_time

    def simulation_step(self):
        self.trader.policy(self.time, self.steps)
        self.time += self.time_delta

    def run(self):
        log.info("Running simulator...")
        self.steps = 0
        while self.time < self.end_time:
            self.simulation_step()
        self.trader.sell_all()
        log.info("Simulation finished:")
        log.info("Ran {} steps from {} to {}.".format(self.steps, start_time, self.time))
        log.info("Trader finished with ${}".format(self.trader.funds))

def main():
    start_time = datetime.datetime.utcnow() - datetime.timedelta(1)
    start_funds = 100.

    market = Market()
    trader = trader(start_funds, market)
    sim = Simulator(trader, start_time, market=market)
    market.setSimulator(sim)
    sim.run()
