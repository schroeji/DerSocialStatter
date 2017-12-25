import datetime

import database
import query
import settings
import util


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
    k = 4
    step_hours = 24
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
    spend = int((self.funds / k) * 100) / 100.
    for i in range(k):
        self.market.buy(gains[i][0], spend)
    return datetime.timedelta(hours=step_hours)

def largest_xhr_policy(self, time, step_nr):
    """
    Buy those k coins which had the biggest percentage gain in the last xhrs.
    Sell all coins which are no top gainers and reinvest the profits.
    """
    k = 4
    step_hours = 3
    start_time = time - datetime.timedelta(hours=step_hours)
    if step_nr == 0:
        self.all_subs = self.market.portfolio.keys()
    else:
        self.market.sell_all()
    gains = query.percentage_price_growths(self.db, self.all_subs, start_time, time)
    spend = int((self.funds / k) * 100) / 100.
    for i in range(k):
        self.market.buy(gains[i][0], spend)
    return datetime.timedelta(hours=step_hours)

def subreddit_growth_policy(self, time, step_nr):
    """
    Buy those k coins which subreddit experienced the biggest growth in the last x hrs.
    """
    k = 4
    x = 12
    if step_nr == 0:
        self.all_subs = self.market.portfolio.keys()
    else:
        self.market.sell_all()
    xhrs =  datetime.timedelta(hours=x)
    start_time = time - xhrs
    end_time = time
    growths = query.sorted_average_growth(self.db, self.all_subs, start_time, end_time)
    growths.reverse()

    # split equally
    spend = int((self.funds / k) * 100) / 100.
    growth_sum = sum([growths[i][1] for i in range(k)])
    funds = self.funds
    for i in range(k):
        # scale spend money realtive with sub growth
        # spend = int((growths[i][1]/growth_sum) * funds * 100) / 100.
        self.market.buy(growths[i][0], spend)
    return xhrs
