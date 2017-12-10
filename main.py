import os.path
from database import DatabaseConnection
from reddit import RedditStats
from coinmarketcap import CoinCap

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

def write_subs_to_file(path, subreddit_list):
    string = "\n".join(subreddit_list)
    f = open("subreddits.txt", "w")
    f.write(string)
    f.close()

def read_subs_from_file(path):
    f = open(path, "r")
    inp = f.read()
    subs = inp.split("\n")
    return subs[:-1]

if __name__ == "__main__":
    file_name = "subreddits.txt"
    if os.path.exists(file_name):
        subs = read_subs_from_file(file_name)
    else :
        subs = create_subreddit_list()
        write_subs_to_file(file_name, subs)

    collect(subs)