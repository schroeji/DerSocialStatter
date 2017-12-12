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

def main():
    db = DatabaseConnection("postgres", "postgres", "asdfgh")
    all_subreddits = db.get_all_subreddits()
    mean_growths = []
    start_time = datetime.datetime.now() - datetime.timedelta(1)
    end_time = datetime.datetime.now()
    for subr in all_subreddits:
        metrics = db.get_metrics_for_subreddit(subr, start=start_time, end=end_time)
        print(metrics)
        if len(metrics) == 2:
            growth = calc_mean_growth(metrics)
            mean_growths.append((subr, growth))

    db.close()

    sorted_growths = sorted(mean_growths, key=lambda subr: subr[1])
    for s in sorted_growths:
        print(s)

if __name__ == "__main__":
    main()
