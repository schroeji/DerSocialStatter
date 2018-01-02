from __future__ import absolute_import, division, print_function

import datetime
import time

import numpy as np

import util
from database import DatabaseConnection
from settings import general

# TODO better error handling
# TODO different timescales

log = util.setup_logger(__file__)

def calc_mean_growth(metrics):
    assert len(metrics) == 2
    growths = []
    for m1, m2 in zip(metrics[0], metrics[1]):
        if m1 == 0 and m2 == 0:
            growths.append(0)
        elif m2 == 0:
            pass
            # TODO maybe there is a better way to handle this case
            # growths.append(m1)
        else:
            growths.append((m1-m2)/m2)
    return np.mean(growths)

def recent_growth(db, subreddits):
    mean_growths = []
    for subr in subreddits:
        metrics = db.get_metrics_for_subreddit(subr)
        if len(metrics) == 2:
            growth = calc_mean_growth(metrics)
            mean_growths.append((subr, growth))
    sorted_growths = sorted(mean_growths, key=lambda subr: subr[1])
    return sorted_growths

def averaged_interval_growth_rate(db, subreddit, start, end, weights=None):
    """
    Calculates the average growth_rate for the for metrics relative to their baseline.
    """
    hour = datetime.timedelta(hours=1)
    total_hours = (end - start).seconds / 3600. + (end-start).days * 24
    time_list = [start + hour*x for x in range(int(total_hours) + 1)]
    metrics = np.array([db.get_interpolated_data(subreddit, timestamp) for timestamp in time_list])
    # calc subscriber rate from data
    subscriber_rate = np.array([metrics[i, 0] - metrics[i-1, 0] for i in range(1, len(metrics))])
    submission_rate = metrics[:, 1]
    comment_rate = metrics[:, 2]
    mention_rate = metrics[:, 3]
    subscriber_rate[0] = max(subscriber_rate[0], 0)
    submission_rate[0] = max(subscriber_rate[0], 0)
    comment_rate[0] = max(subscriber_rate[0], 0)
    mention_rate[0] = max(subscriber_rate[0], 0)
    # calc the growth for the given rates
    subscriber_rate_growth =  (sum(subscriber_rate) + total_hours) / (total_hours * (subscriber_rate[0] + 1))
    submission_rate_growth = (sum(submission_rate) + total_hours) / (total_hours * (submission_rate[0] + 1))
    comment_rate_growth = (sum(comment_rate) + total_hours) / (total_hours * (comment_rate[0] + 1))
    mention_rate_growth = (sum(mention_rate) + total_hours) / (total_hours * (mention_rate[0] + 1))
    # return np.average([subscriber_rate_growth, submission_rate_growth, comment_rate_growth, mention_rate_growth], weights=weights)
    return np.array([subscriber_rate_growth, submission_rate_growth, comment_rate_growth, mention_rate_growth])

def sub_and_price_growths(db, coin_name_array, end, hours=24, include_future_growth=True):
    """
    Collects the average interval growths and outputs them together with
    the percentage gain of the coin in the next 24h AFTER end.
    """
    start = end - datetime.timedelta(hours=hours)
    growth_time = end + datetime.timedelta(hours=hours)
    data = []
    for coin in coin_name_array:
        row = averaged_interval_growth_rate(db, coin[-1], start, end)
        # add growth in last 24hrs
        row = np.append(row, db.get_interpolated_price_data(coin[-1], end)[2])
        # add growth in next 24hrs (prediction target)
        if include_future_growth:
            row = np.append(row, db.get_interpolated_price_data(coin[-1], growth_time)[2])
        log.info("{} {}".format(coin[-1], row))
        data.append(row)
    data = np.array(data)
    return data

def prep_training_data(db, coin_name_array, timestep, steps):
    hour_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    end_list = [hour_ago - timestep*i for i in range(1, steps+1)]
    for end in end_list:
        data = sub_and_price_growths(db, coin_name_array, end, include_future_growth=True)
        util.export_to_csv("data.csv", data, append=True)

def prep_prediction_data(db, coin_name_array):
    growths = sub_and_price_growths(db, coin_name_array, datetime.datetime.utcnow(), include_future_growth=False)
    preds = []
    means = []
    for i,c in enumerate(growths):
        l = list(c)
        l.insert(0, coin_name_array[i][0])
        preds.append(l)
        means.append([coin_name_array[i][0], np.mean(c[:-1])])
    sorted_means= sorted(means, key=lambda subr: subr[1])
    print(sorted_means)
    util.export_to_csv("pred.csv", preds, append=False)

def percentage_price_growths(db, subreddits, start, end, sort=True):
    price_data = db.get_all_price_data_in_interval(start, end)
    result = []
    for sub in subreddits:
        # find first price
        found_row = False
        for row in price_data:
            if row[0] == sub:
                price1 = row[1]
                found_row = True
                break
        if not found_row:
            log.warn("No price data for {} in interval {} to {}".format(sub, start, end))
            continue
            # raise ValueError("No price data for {} in interval {} to {}".format(sub, start, end))

        # find last price
        for row in reversed(price_data):
            if row[0] == sub:
                price2 = row[1]
                break
        result.append([sub, (price2 - price1) / price1 * 100])
    if sort:
        result = sorted(result, key=lambda subr: subr[1])
    return result

def average_growth(db, subreddits, start_time, end_time, sort=True):
    """
    Returns the subreddit with the biggest (relative) mean growth in the last 12hrs.
    Calculates the growth for the interval timestamp - hours until timestamp.
    """
    data_points = db.get_all_data_in_interval(start_time, end_time)
    result = []
    for sub in subreddits:
        # find first price
        found_row = False
        for row in data_points:
            if row[0] == sub:
                metrics1 = row[1:5]
                found_row = True
                break
        if not found_row:
            log.warn("No subreddit data for {} in interval {} to {}".format(sub, start_time, end_time))
            continue
            # raise ValueError("No price data for {} in interval {} to {}".format(sub, start, end))
        # find last price
        for row in reversed(data_points):
            if row[0] == sub:
                metrics2 = row[1:5]
                break
        result.append([sub, calc_mean_growth([metrics1, metrics2])])
    if sort:
        result = sorted(result, key=lambda subr: subr[1])
    return result

def covariance(db, subreddits):
    days = 1
    delta = datetime.timedelta(hours=12)
    start_time = datetime.datetime.utcnow() - datetime.timedelta(days)
    end_time = start_time + delta
    sub_growths = []
    price_growths = []
    for i in range(days):
        sub_growths += [g[1] for g in average_growth(db, subreddits, start_time, end_time, sort=False)]
        price_growths += [p[1] for p in percentage_price_growths(db, subreddits, start_time + delta, end_time + delta, sort=False)]
        start_time += delta
        end_time += delta
    print(sub_growths)
    print(price_growths)
    sub_growths = np.array(sub_growths)*100
    price_growths = np.array(price_growths)
    arr = np.vstack((sub_growths, price_growths))
    print(np.cov(arr))

def main():
    # coin_name_array = util.read_subs_from_file(general["subreddit_file"])
    coin_name_array = util.read_subs_from_file(general["binance_file"])
    auth = util.get_postgres_auth()
    db = DatabaseConnection(**auth)
    # all_subreddits = db.get_all_subreddits()
    all_subreddits = [coin[-1] for coin in coin_name_array]
    start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    # end_time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    end_time = datetime.datetime.utcnow()
    # growths = percentage_price_growths(db, all_subreddits, start_time, end_time)
    growths = average_growth(db, all_subreddits, start_time, end_time)
    print(growths)
    # covariance(db, all_subreddits)
    db.close()

if __name__ == "__main__":
    main()
