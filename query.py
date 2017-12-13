from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from database import DatabaseConnection
from settings import postgres as pg
import numpy as np
import datetime
import matplotlib
import matplotlib.pyplot as plt


# TODO better error handling
# TODO different timescales


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

def plot_growth(db, subreddit_list, start=None, end=None):
    if start is None:
        start = datetime.datetime.now() - datetime.timedelta(1)
    if end is None:
        end = datetime.datetime.now()
    assert start < end
    print(subreddit_list)
    for subr in subreddit_list:
        list_of_dates = []
        growths = []
        m = db.get_rows_for_subreddit(subr, start=start, end=end)
        m.reverse()
        if (len(m) <= 2):
            print("Not enough data points in interval for {}.".format(subr))
            continue
        list_of_dates.append(m[0][0])
        growths.append(0)
        for i in range(1, len(m)):
            list_of_dates.append(m[i][0])
            growths.append(growths[-1] + calc_mean_growth([m[i][2:], m[i-1][2:]]))
        dates = matplotlib.dates.date2num(list_of_dates)
        plt.plot_date(dates, growths, "-", label=subr)
    plt.legend()
    plt.show()

def main():
        db = DatabaseConnection(pg["database"], pg["user"], pg["password"], pg["hostname"])
    all_subreddits = db.get_all_subreddits()
    start =  datetime.datetime.now() - datetime.timedelta(hours=12)
    end =  datetime.datetime.now()- datetime.timedelta(hours=0)
    sorted_subs = growth_in_interval(db, all_subreddits, start, end)
    # print(sorted_subs)
    plot_growth(db, [s[0] for s in sorted_subs[-10:]], start, end)
    # recent_growth(db, ["ripple"])
    db.close()

if __name__ == "__main__":
    main()
