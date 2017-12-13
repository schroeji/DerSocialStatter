import os

filedir = os.path.dirname(os.path.realpath(__file__))

#general settings
general = dict(
    subreddit_file = os.path.join(filedir, "subreddits.csv"),
    log_file = os.path.join(filedir, "log.log"),
    auth_file = os.path.join(filedir, "auth.json")
)

