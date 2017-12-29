import datetime

import database
import query
import settings
import util

SCALE_SPENDINGS = False
K = 4
STEP_HOURS = 12
#if SCALE_SPENDINGS = True this will prevent errors for negative growths/gains
USE_SMOOTHING = True


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
    gains.reverse()
    if SCALE_SPENDINGS:
        if USE_SMOOTHING and gains[K-1][1] < 0:
            for i in range(K):
                # => smallest gain will be 1 and the rest is adjusted accordingly
                gains[i][1] += -gains[K-1][1] + 1
        gains_sum = sum([gains[i][1] for i in range(K)])
        funds = self.funds
    else:
        spend = int((self.funds / K) * 100) / 100.
    for i in range(K):
        if SCALE_SPENDINGS:
            spend = int((gains[i][1]/gains_sum) * funds * 100) / 100.
            if spend == 0:
                continue
        print(spend)
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
    gains.reverse()
    if SCALE_SPENDINGS:
        # maybe negative => problematic scaling and bugs
        # solve with smoothing
        if USE_SMOOTHING and gains[K-1][1] < 0:
            for i in range(K):
                # => smallest gain will be 1 and the rest is adjusted accordingly
                gains[i][1] += -gains[K-1][1] + 1
        gains_sum = sum([gains[i][1] for i in range(K)])
        funds = self.funds
    else:
        spend = int((self.funds / K) * 100) / 100.
    for i in range(K):
        if SCALE_SPENDINGS:
            spend = int((gains[i][1]/gains_sum) * funds * 100) / 100.
            if spend == 0:
                continue
        self.market.buy(gains[i][0], spend)
    return datetime.timedelta(hours=STEP_HOURS)

def subreddit_growth_policy(self, time, step_nr):
    """
    Buy those K coins with the biggest subbreddit grwoth in the last STEP_HOURS hours.
    """
    if step_nr == 0:
        self.all_subs = self.market.portfolio.keys()
    else:
        self.market.sell_all()
    xhrs =  datetime.timedelta(hours=STEP_HOURS)
    start_time = time - xhrs
    end_time = time
    growths = query.average_growth(self.db, self.all_subs, start_time, end_time)
    growths.reverse()

    # split equally
    if SCALE_SPENDINGS:
        if USE_SMOOTHING and growths[K-1][1] < 0:
            for i in range(K):
                # => smallest gain will be 1 and the rest is adjusted accordingly
                growths[i][1] += -growths[K-1][1] + 1
        growth_sum = sum([growths[i][1] for i in range(K)])
        funds = self.funds
    else:
        spend = int((self.funds / K) * 100) / 100.
    for i in range(K):
        # scale spend money realtive with sub growth
        if SCALE_SPENDINGS:
            spend = int((growths[i][1]/growth_sum) * funds * 100) / 100.
            if spend == 0:
                continue
        self.market.buy(growths[i][0], spend)
    return xhrs
