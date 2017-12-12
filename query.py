from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from database import DatabaseConnection
import numpy as np
import datetime


# TODO better error handling
# TODO different timescales


def calc_mean_growth(metrics):
    assert len(metrics) == 2
    growths = []
    for m1, m2 in zip(metrics[0], metrics[1]):
        if m1 == 0 and m2 == 0:
            growths.append(0)
        elif m2 == 0:
            # TODO maybe there is a better way to handle this case
            growths.append(m1)
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
    for s in sorted_growths:
        print(s)

def growth_in_interval(db, subreddits, start, end):
    mean_growths = []
    for subr in subreddits:
        m = db.get_metrics_for_subreddit(subr, start=start, end=end)
        if len(m) >= 2:
            metrics = [m[0], m[-1]]  #newest and oldest element in interval
            growth = calc_mean_growth(metrics)
            mean_growths.append((subr, growth))
    sorted_growths = sorted(mean_growths, key=lambda subr: subr[1])
    for s in sorted_growths:
        print(s)


def main():
    db = DatabaseConnection("postgres", "postgres", "asdfgh", "192.168.178.63")
    all_subreddits = db.get_all_subreddits()
    # recent_growth(db, all_subreddits)
    start =  datetime.datetime.now() - datetime.timedelta(hours=24)
    end =  datetime.datetime.now() - datetime.timedelta(hours=8)
    growth_in_interval(db, all_subreddits, start, end)
    db.close()

if __name__ == "__main__":
    main()
