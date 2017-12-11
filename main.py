<<<<<<< HEAD
import os
import sys
import argparse
import datetime
from database import DatabaseConnection
from reddit import RedditStats
from coinmarketcap import CoinCap

def collect(subreddit_list):
    stat = RedditStats()
    db = DatabaseConnection("postgres", "postgres", "asdfgh")
    start = datetime.datetime.now() - datetime.timedelta(hours=1)
    start = start.strftime("%s")
    for subreddit in subreddit_list:
        db.insert(stat.compile_dict(subreddit, start))
        print("Got stats for:", subreddit)
    db.close()

def create_subreddit_list(num):
    """
    create a list of crypto coin subreddits
    """
    stat = RedditStats()
    coincap = CoinCap()
    names = coincap.get_coin_names(num)
    # remove special characters
    for i, name in enumerate(names):
        names[i] = "".join(x for x in name if x.isalnum())
    subreddit_list = stat.find_subreddits(names)
    return subreddit_list

def write_subs_to_file(path, subreddit_list):
    string = "\n".join(subreddit_list)
    f = open(path, "w")
    f.write(string)
    f.close()

def read_subs_from_file(path):
    f = open(path, "r")
    inp = f.read()
    subs = inp.split("\n")
    return subs[:-1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--find_subs", default=0, type=int, action='store',
                        help="Find crypto coin subreddits (overwrites subreddits.txt).")
    parser.add_argument("--recreate_table", default=False, action='store_true',
                        help="Delete and recreate the data table.")
    parser.add_argument("--collect", default=False, action='store_true',
                        help="Collect subreddit information into the database.")
    args = parser.parse_args()
    # -----------------------------------

    file_name = "/subreddits.txt"
    path = os.path.dirname(os.path.realpath(__file__))
    file_path = path + file_name
    if args.find_subs > 0:
        subs = create_subreddit_list(args.find_subs)
        write_subs_to_file(file_path, subs)

    if args.recreate_table:
        db = DatabaseConnection("postgres", "postgres", "asdfgh")
        db.delete_table()
        db.create_table()
        db.close()

    if args.collect:
        if os.path.exists(file_path):
            subs = read_subs_from_file(file_path)
            collect(subs)
        else :
            print("Collect called but {} does not exist.".format(file_name))
            print("Run --find_subs first.")


if __name__ == "__main__":
    main()