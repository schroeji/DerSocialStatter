import os
#general settings
general = dict(
    subreddit_file = os.path.dirname(os.path.realpath(__file__)) + "/subreddits.csv"
)
#postgres settings
postgres = dict(
    user = "postgres",
    password = "pass",
    database = "postgres",
    hostname = "localhost"
)

reddit = dict(
    auth_file = os.path.dirname(os.path.realpath(__file__)) + "/auth.json"
)