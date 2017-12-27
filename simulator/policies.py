import datetime

import database
import query
import settings
import util

SCALE_SPENDINGS = True
K = 4
STEP_HOURS = 12

def raiblocks_yolo_policy(self, time, step_nr):
    """
    Buy full raiblocks and hold until the end.
    """
    if step_nr == 0:
        self.market.buy("raiblocks", self.funds)
    return datetime.timedelta(hours=24)

def largest_24h_increase_policy(self, time, step_nr):
    """
    Buy those k coins which had the biggest percentage gain in the last 24hrs.
    Sell all coins which are no top gainers and reinvest the profits.
    """
    if step_nr == 0:
        self.all_subs = self.market.portfolio.keys()
    else:
        self.market.sell_all()
    gains = []
    for coin in self.all_subs:
        try:
            gain = self.db.get_interpolated_price_data(coin, time)
        except ValueError:
            continue
        if gain == [] or gain is None:
            continue
        gains.append([coin, gain[2]])
    gains = sorted(gains, key=lambda subr: subr[1])
    if SCALE_SPENDINGS:
        gains_sum = sum([gains[i][1] for i in range(K)])
        funds = self.funds
    else:
        spend = int((self.funds / K) * 100) / 100.
    for i in range(k):
        if SCALE_SPENDINGS:
            spend = int((gains[i][1]/gains_sum) * funds * 100) / 100.
        self.market.buy(gains[i][0], spend)
    return datetime.timedelta(hours=STEP_HOURS)

def largest_xhr_policy(self, time, step_nr):
    """
    Buy those k coins which had the biggest percentage gain in the last xhrs.
    Sell all coins which are no top gainers and reinvest the profits.
    """
    start_time = time - datetime.timedelta(hours=STEP_HOURS)
    if step_nr == 0:
        self.all_subs = self.market.portfolio.keys()
    else:
        self.market.sell_all()
    gains = query.percentage_price_growths(self.db, self.all_subs, start_time, time)
    spend = int((self.funds / k) * 100) / 100.
    for i in range(K):
        self.market.buy(gains[i][0], spend)
    return datetime.timedelta(hours=STEP_HOURS)

def subreddit_growth_policy(self, time, step_nr):
    """
    Buy those k coins which subreddit experienced the biggest growth in the last x hrs.
    """
    if step_nr == 0:
        self.all_subs = self.market.portfolio.keys()
    else:
        self.market.sell_all()
    xhrs =  datetime.timedelta(hours=STEP_HOURS)
    start_time = time - xhrs
    end_time = time
    growths = query.sorted_average_growth(self.db, self.all_subs, start_time, end_time)
    growths.reverse()

    # split equally
    if SCALE_SPENDINGS:
        growth_sum = sum([growths[i][1] for i in range(K)])
        funds = self.funds
    else:
        spend = int((self.funds / k) * 100) / 100.
    for i in range(k):
        # scale spend money realtive with sub growth
        if SCALE_SPENDINGS:
            spend = int((growths[i][1]/growth_sum) * funds * 100) / 100.
        self.market.buy(growths[i][0], spend)
    return xhrs
