import datetime

import query
import util
from database import DatabaseConnection

log = util.setup_logger(__name__)
auth = util.get_postgres_auth()
db = DatabaseConnection(**auth)


K = 4
SCALE_SPENDINGS = False


def __sell_and_spendings__(adapter, growths):
    """
    Calculates which coins to sell and how much o spend on other coins based on a dict of growths and subreddits.
    """
    assert len(growths) == K
    net_worth = adapter.get_net_worth()
    buy_coins = [util.get_symbol_for_sub(adapter.get_coins(), g[0]) for g in growths[:K]]
    owned_coins = adapter.get_portfolio_funds_value()
    owned_coins.pop(adapter.mode, None)
    spend = {}
    if SCALE_SPENDINGS:
        if growths[K-1][1] < 0:
            for i in range(K):
                # smallest grwoth will be 1 and the rest is adjusted accordingly
                # => smoothed and no negative values
                growths[i][1] += -growths[K-1][1] + 1
        growths_sum = sum([growths[i][1] for i in range(K)])
        for i, coin in enumerate(buy_coins):
            spend[coin] = (growths[i][1]/growths_sum) * net_worth
    else:
        for coin in buy_coins:
            spend[coin] = net_worth / K
    # prevent selling and rebuying the same coin
    sell = list(owned_coins.keys())
    for coin, amount in spend.items():
        if coin in sell:
            log.info("Already owning %s%s of %s" % (owned_coins[coin], adapter.mode, coin))
            log.info("Prevented sell and rebuy")
            sell.remove(coin)
            if amount > owned_coins[coin]:
                spend[coin] = amount - owned_coins[coin]
            else:
                spend[coin] = 0
            available = owned_coins[coin]
            # redistribute additionally available equally funds
            for redis_coin in buy_coins:
                if redis_coin == coin:
                    continue
                else:
                    spend[redis_coin] += 1./(K-1) * available
    # remove sells when total would be under threshold
    for coin, _ in owned_coins.items():
        if owned_coins[coin] < adapter.get_min_spend():
            sell.remove(coin)
    # remove buys when total would be under threshold
    for coin in list(spend.keys()):
        if spend[coin] < adapter.get_min_spend():
            spend.pop(coin, None)
    return (sell, spend)


def subreddit_growth_policy(adapter):
    trade_hours = 22
    growth_hours = 23
    now = datetime.datetime.utcnow()
    last_trade = adapter.get_last_trade_date()
    if last_trade > now - datetime.timedelta(hours=trade_hours):
        log.info("Not trading because last trade is less than %s hours old." % (trade_hours))
        return
    start_time = now - datetime.timedelta(hours=growth_hours)
    subs = [coin[-1] for coin in adapter.get_coins()]
    growths = query.average_growth(db, subs, start_time, now, sort=True)
    growths.reverse()
    sell, spend = __sell_and_spendings__(adapter, growths[:K])
    log.info("Selling: %s" % (sell))
    log.info("Buying: %s" % (spend.keys()))
    for coin in sell:
        adapter.sell_all(coin)
    for coin, amount in spend.items():
        adapter.buy_by_symbol(coin, amount)
