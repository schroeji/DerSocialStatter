from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from database import DatabaseConnection
import numpy as np
import datetime
import matplotlib
import matplotlib.pyplot as plt
import util
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

def growth_in_interval(db, subreddits, start, end):
    mean_growths = []
    for subr in subreddits:
        m = db.get_metrics_for_subreddit(subr, start=start, end=end)
        if len(m) >= 2:
            metrics = [m[0], m[-1]]  #newest and oldest element in interval
            growth = calc_mean_growth(metrics)
            mean_growths.append((subr, growth))
    sorted_growths = sorted(mean_growths, key=lambda subr: subr[1])
    return sorted_growths


def plot_growth(db, subreddit_list, start=None, end=None, with_respect_to_begin=False):
    if start is None:
        start = datetime.datetime.utcnow() - datetime.timedelta(1)
    if end is None:
        end = datetime.datetime.utcnow()
    assert start < end
    log.info(subreddit_list)
    for subr in subreddit_list:
        list_of_dates = []
        growths = []
        m = db.get_rows_for_subreddit(subr, start=start, end=end)
        m.reverse()
        if (len(m) <= 2):
            log.info("Not enough data points in interval for %s." % (format(subr)))
            continue
        list_of_dates.append(m[0][0])
        growths.append(0)
        for i in range(1, len(m)):
            list_of_dates.append(m[i][0])
            current_val = m[i][2:]
            if with_respect_to_begin:
                compare_val = m[0][2:]
                growths.append(calc_mean_growth([current_val, compare_val]))
            else:
                compare_val = m[i-1][2:]
                growths.append(growths[-1] + calc_mean_growth([current_val, compare_val]))
        dates = matplotlib.dates.date2num(list_of_dates)
        plt.plot_date(dates, growths, "-", label=subr)
    plt.legend()
    plt.show()

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
    # cal the grwoth for the given rates
    subscriber_rate_growth =  (sum(subscriber_rate) + total_hours) / (total_hours * (subscriber_rate[0] + 1))
    submission_rate_growth = (sum(submission_rate) + total_hours) / (total_hours * (submission_rate[0] + 1))
    comment_rate_growth = (sum(comment_rate) + total_hours) / (total_hours * (comment_rate[0] + 1))
    mention_rate_growth = (sum(mention_rate) + total_hours) / (total_hours * (mention_rate[0] + 1))
    # return np.average([subscriber_rate_growth, submission_rate_growth, comment_rate_growth, mention_rate_growth], weights=weights)
    return np.array([subscriber_rate_growth, submission_rate_growth, comment_rate_growth, mention_rate_growth])

def sub_and_price_growths(db, coin_name_array, end, include_future_growth=True):
    """
    Collects the average interval growths and outputs them together with
    the percentage gain of the coin in the next 24h AFTER end.
    """
    start = end - datetime.timedelta(hours=24)
    growth_time = end + datetime.timedelta(hours=24)
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

def main():
    auth = util.get_postgres_auth()
    db = DatabaseConnection(**auth)
    # all_subreddits = db.get_all_subreddits()
    coin_name_array = util.read_subs_from_file(general["subreddit_file"])
    coin_name_array = coin_name_array[10:] # skip recently added
    prep_training_data(db, coin_name_array, datetime.timedelta(hours=24), 1)
    prep_prediction_data(db, coin_name_array)
    db.close()

if __name__ == "__main__":
    main()
