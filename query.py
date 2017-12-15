from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from database import DatabaseConnection
import numpy as np
import datetime
import matplotlib
import matplotlib.pyplot as plt
import util


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
        start = datetime.datetime.now() - datetime.timedelta(1)
    if end is None:
        end = datetime.datetime.now()
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
    total_hours = (end - start).seconds / 3600.
    time_list = [start + hour*x for x in range(int(total_hours) + 1)]
    metrics = np.array([db.get_interpolated_data(subreddit, timestamp) for timestamp in time_list])
    # calc subscriber rate from data
    subscriber_rate = np.array([metrics[i, 0] - metrics[i-1, 0] for i in range(1, len(metrics))])
    submission_rate = metrics[:, 1]
    comment_rate = metrics[:, 2]
    mention_rate = metrics[:, 3]
    # cal the grwoth for the given rates
    subscriber_rate_growth =  (sum(subscriber_rate) + total_hours) / (total_hours * (subscriber_rate[0] + 1))
    submission_rate_growth = (sum(submission_rate) + total_hours) / (total_hours * (submission_rate[0] + 1))
    comment_rate_growth = (sum(metrics[:, 2]) + total_hours) / (total_hours * (comment_rate[0] + 1))
    mention_rate_growth = (sum(metrics[:, 3]) + total_hours) / (total_hours * (mention_rate[0] + 1))
    # return np.average([subscriber_rate_growth, submission_rate_growth, comment_rate_growth, mention_rate_growth], weights=weights)
    return [subscriber_rate_growth, submission_rate_growth, comment_rate_growth, mention_rate_growth]

def main():
    auth = util.get_postgres_auth()
    db = DatabaseConnection(**auth)
    all_subreddits = db.get_all_subreddits()
    all_subreddits.remove("ecoin")
    start =  datetime.datetime.now() - datetime.timedelta(hours=37)
    end =  datetime.datetime.now() - datetime.timedelta(hours=25)
    time =  datetime.datetime.now() - datetime.timedelta(hours=1)
    ap = db.get_all_subreddits_price()

    sorted_subs = growth_in_interval(db, all_subreddits, start, end)
    # log.info(sorted_subs)
    # plot_growth(db, [s[0] for s in sorted_subs[-10:]], start, end, with_respect_to_begin=True)
    # print(sorted_subs[-10:])
    # growths = [(subreddit, averaged_interval_growth_rate(db, subreddit, start, end, weights=[0.15, 0.15, 0.4, 0.3])) for subreddit in all_subreddits ]
    # growths = [averaged_interval_growth_rate(db, subreddit, start, end) for subreddit in all_subreddits ]
    # prices = [db.get_interpolated_price_data(subreddit, time) for subreddit in all_subreddits]
    # print(len(prices))
    # print(len(growths))

    db.close()


if __name__ == "__main__":
    main()
