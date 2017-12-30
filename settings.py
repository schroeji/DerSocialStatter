import os

filedir = os.path.dirname(os.path.realpath(__file__))

#general settings
general = dict(
    subreddit_file = os.path.join(filedir, "subreddits.csv"),
    binance_file = os.path.join(filedir, "binance.csv"),
    poloniex_file = os.path.join(filedir, "poloniex.csv"),
    log_file = os.path.join(filedir, "log.log"),
    auth_file = os.path.join(filedir, "auth.json")
)
