import os

filedir = os.path.dirname(os.path.realpath(__file__))
csvdir = os.path.join(filedir, "csv")

#general settings
general = dict(
    subreddit_file=os.path.join(csvdir, "subreddits.csv"),
    binance_file=os.path.join(csvdir, "binance.csv"),
    poloniex_file=os.path.join(csvdir, "poloniex.csv"),
    bittrex_file=os.path.join(csvdir, "bittrex.csv"),
    log_file=os.path.join(filedir, "log.log"),
    auth_file=os.path.join(filedir, "auth.json"),
)

#reddit settings
reddit = dict(
    general_subs=["cryptocurrency", "cryptotrading",
                  "cryptotrade", "cryptomarkets",
                  "cryptowallstreet", "darknetmarkets", "altcoin"]
)

#simulator settings
simulator = dict(
    scale_spendings=False,
    k=4,
    step_hours=33,
    growth_hours=12,
    use_smoothing=True
)

#autotrader settings
autotrade = dict(
    k=4,
    growth_hours=24,
    min_hold_hours=7,
    use_stagnation_detection=True,
    stagnation_hours=3,
    stagnation_threshold=0.005,
    never_sell=["BNB", "XRB", "NANO"],
    use_dynamic_stagnation_detection=True,
    dynamic_top_nr=20,
    dry_run=False
)
