from database import DatabaseConnection
from reddit import RedditStats
from coinmarketcap import CoinCap

# subreddit_list = ["dogecoin", "iota", "litecoin", "monero", "nem", "potcoin", "substratumnetwork"]

def collect(subreddit_list):
    stat = RedditStats()
    db = DatabaseConnection("postgres", "postgres")
    for subreddit in subreddit_list:
        db.insert(stat.compile_dict(subreddit))
        print("Got stats for:", subreddit)
    db.close()

def create_subreddit_list():
    """
    create a list of crypto coin subreddits
    """
    stat = RedditStats()
    coincap = CoinCap()
    names = coincap.get_coin_names(200)
    # remove special characters
    for i, name in enumerate(names):
        names[i] = "".join(x for x in name if x.isalnum())
    subreddit_list = stat.find_subreddits(names)
    return subreddit_list

if __name__ == "__main__":
    subs = create_subreddit_list()
    collect(subs)
