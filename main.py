import os
import argparse
import datetime
from settings import general
import util
from database import DatabaseConnection
from reddit import RedditStats
from coinmarketcap import CoinCap

log = util.setup_logger(__name__)

def collect(coin_name_array):
    """
    Collects the reddit data for the coins in coin_name_array.
    coin_name_array should be a 2D array where each row contains keywords for a crypto coin
    and the last one is the subreddit
    """
    stat = RedditStats()
    auth = util.get_postgres_auth()
    db = DatabaseConnection(**auth)
    start = datetime.datetime.now() - datetime.timedelta(hours=1)
    start = start.strftime("%s")
    general_subs = ["cryptocurrency", "cryptotrading", "cryptotrade", "cryptomarkets", "cryptowallstreet", "darknetmarkets", "altcoin"]
    mentions = stat.get_mentions(coin_name_array, general_subs, start, True)
    log.info("Got mentions for all subs.")
    for i, coin_tuple in enumerate(coin_name_array):
        subreddit = coin_tuple[-1]
        stats_dict = stat.compile_dict(subreddit, start)
        stats_dict["mentions"] = mentions[i]
        db.insert_data(stats_dict)
        log.info("Got stats for: %s" % (subreddit))
    db.close()


def collect_price(coin_name_array):
    """
    Collects the price data for the coins in coin_name_list.
    """
    auth = util.get_postgres_auth()
    db = DatabaseConnection(**auth)
    cap = CoinCap()
    time = datetime.datetime.now()
    # time = time.strftime("%s")
    price_data = cap.get_coin_price_data([c[0] for c in coin_name_array])
    for k, d in price_data.items():
        d["time"] = time
        for coin in coin_name_array:
            if k in coin:
                d["subreddit"] = coin[-1]
        db.insert_price(d)
        log.info("Got price for: %s" % (d["subreddit"]))
    db.close()

def create_coin_name_array(num):
    """
    create a list of crypto currencies with their subreddits
    returns a list of dimensions n x 4 where
    n <= count is the number of subreddits found and each entry is ofthe format:
    id,name,symbol,subreddit
    """
    stat = RedditStats()
    coincap = CoinCap()
    coin_name_array = coincap.get_coin_aliases(num)
    # remove special characters and add as subreddit name
    for coin_tuple in coin_name_array:
        coin_tuple.append("".join(x for x in coin_tuple[0] if x.isalnum()))
    subreddit_list = stat.find_subreddits([name[-1] for name in coin_name_array])
    #remove coins without a subreddit
    return_array = [coin_tuple for coin_tuple in coin_name_array if coin_tuple[-1] in subreddit_list]
    return return_array

def main():
    file_path = general["subreddit_file"]
    parser = argparse.ArgumentParser()
    parser.add_argument("--find_subs", default=0, type=int, action='store',
                        help="Find crypto coin subreddits (overwrites {}).".format(file_path))
    parser.add_argument("--recreate_table", default=False, action='store_true',
                        help="Delete and recreate the data table.")
    parser.add_argument("--collect", default=False, action='store_true',
                        help="Collect subreddit information into the database.")
    parser.add_argument("--collect_price", default=False, action='store_true',
                        help="Collect coin price information into the database.")
    args = parser.parse_args()
    # -----------------------------------

    if args.find_subs > 0:
        subs = create_coin_name_array(args.find_subs)
        util.write_subs_to_file(file_path, subs)

    if args.recreate_table:
        auth = util.get_postgres_auth()
        db = DatabaseConnection(**auth)
        db.delete_data_table()
        db.create_data_table()
        db.close()

    if args.collect:
        if os.path.exists(file_path):
            subs = util.read_subs_from_file(file_path)
            collect(subs)
        else :
            log.info("Collect called but %s does not exist." % (file_path))
            log.info("Run --find_subs first.")

    if args.collect_price:
        if os.path.exists(file_path):
            subs = util.read_subs_from_file(file_path)
            collect_price(subs)
        else :
            log.info("Collect price called but %s does not exist." % (file_path))
            log.info("Run --find_subs first.")

if __name__ == "__main__":
    main()
