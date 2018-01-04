import os

filedir = os.path.dirname(os.path.realpath(__file__))
csvdir = os.path.join(filedir, "csv")

#general settings
general = dict(
    subreddit_file = os.path.join(csvdir, "subreddits.csv"),
    binance_file = os.path.join(csvdir, "binance.csv"),
    poloniex_file = os.path.join(csvdir, "poloniex.csv"),
    bittrex_file = os.path.join(csvdir, "bittrex.csv"),
    log_file = os.path.join(filedir, "log.log"),
    auth_file = os.path.join(filedir, "auth.json")
)
