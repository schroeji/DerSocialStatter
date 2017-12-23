import datetime

import database
import query


def raiblocks_yolo_policy(self, time, step_nr):
    """
    Buy full raiblocks and hold until the end.
    """
    if step_nr == 0:
        self.market.buy(self, "raiblocks", self.funds)
    return datetime.timedelta(hours=24)

def largest_24h_increase_policy(self, time, step_nr):
    """
    Buy those k coins which had the biggest percentage gain in the last 24hrs.
    Sell all coins which are no top gainers and reinvest the profits.
    """
    k = 4
    step_hours = 24
    if step_nr == 0:
        self.all_subs = self.db.get_all_subreddits()
    else:
        self.market.sell_all(self)
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
        self.market.buy(self, gains[i][0], spend)

    return datetime.timedelta(hours=step_hours)
