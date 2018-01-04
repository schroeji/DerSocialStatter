import datetime

import matplotlib.pyplot as plt
import numpy as np

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
        self.networth_history = []
        self.date_history = []

    def simulation_step(self):
        port_val = self.market.portfolio_value()
        self.networth_history.append(self.trader.funds + port_val)
        self.date_history.append(self.time)
        if self.verbose:
            log.info("Time: {}".format(self.time))
            log.info("Coin value: {:8.2f}".format(port_val))
            log.info("funds: {:13.2f}".format(self.trader.funds))
            log.info("Sum: {:15.2f}".format(self.trader.funds + port_val))
        self.time += self.trader.policy(self.trader, self.time, self.steps)
        self.steps += 1

    def run(self):
        log.info("Running simulator...")
        self.steps = 0
        while self.time < self.end_time:
            self.simulation_step()

        self.market.sell_all()
        self.networth_history.append(self.trader.funds)
        self.date_history.append(self.time)
        log.info("Simulation finished:")
        log.info("Ran {} steps from {} to {}.".format(self.steps, self.start_time, self.time))
        log.info("Trader finished with {:8.2f}.".format(self.trader.funds))

def average_percentage_gain(networth_history):
    gains = []
    for i in range(1, len(networth_history)):
        gains.append((networth_history[i] - networth_history[i - 1]) / networth_history[i - 1])
    gains = np.array(gains) * 100
    print(gains)
    return np.mean(gains)

def simulate(policy_list, start_time):
    """
    Function which sets up and runs the simulator.
    """
    auth = util.get_postgres_auth()
    db = database.DatabaseConnection(**auth)
    avg_percentage_gains = {}
    for policy in policy_list:
        log.info("------ {} ------".format(policy.__name__))
        start_funds = 100.
        # market = Market(db)
        # market = Market.create_binance_market(db)
        # market = Market.create_poloniex_market(db)
        market = Market.create_bittrex_market(db)
        trader = Trader(db, start_funds, market)
        trader.policy = policy
        sim = Simulator(trader, start_time, market=market)
        market.setSimulator(sim)
        market.setTrader(trader)
        sim.run()
        avg_percentage_gains[policy.__name__] = average_percentage_gain(sim.networth_history)
        plt.plot_date(sim.date_history, sim.networth_history, "-", label=policy.__name__)

    plt.legend()
    plt.show()
    print(avg_percentage_gains)
