from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from database import DatabaseConnection
import numpy as np
import argparse
import datetime
import util


def calc_mean_growth(features_old, features_new):
    growths = []
    for fold, fnew in zip(features_old, features_new):
        if fold == 0 and fnew == 0:
            growths.append(0)
        elif fold == 0:
            pass
            # TODO maybe there is a better way to handle this case
            # growths.append(m1)
        else:
            growths.append((fnew-fold)/fold)
    return np.mean(growths)

def get_growths(db, subreddits, end_time, hours):
    reference_time = end_time - datetime.timedelta(hours=hours)

    growths = []
    for subr in subreddits:
        reference_data = db.get_interpolated_data(subr, reference_time)
        end_data = db.get_interpolated_data(subr, end_time)
        growth = calc_mean_growth(features_old=reference_data, features_new=end_data)
        growths.append((subr, growth))

    sorted_growths = sorted(growths, key=lambda subr: subr[1])
    return sorted_growths


def main():
    parser = argparse.ArgumentParser(description="Simple Query")
    parser.add_argument('hours', metavar='h', type=float)
    args = parser.parse_args()

    auth = util.get_postgres_auth()
    db = DatabaseConnection(**auth)

    cur_utc = datetime.datetime.utcnow()
    subreddits = db.get_subreddits_with_data(cur_utc-datetime.timedelta(hours=args.hours))

    growths = get_growths(db, subreddits, datetime.datetime.utcnow(), args.hours)
    for g in growths:
        print(g)
    db.close()


if __name__ == "__main__":
    main()
