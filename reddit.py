import datetime
import re

import numpy as np
import praw

import util
from coinmarketcap import CoinCap
from settings import general

log = util.setup_logger(__name__)

HOUR_IN_SECONDS = 3600
GENERAL_SUBS = ["cryptocurrency", "cryptotrading", "cryptotrade", "cryptomarkets", "cryptowallstreet", "darknetmarkets", "altcoin"]

class RedditStats(object):

    def __init__(self, hours=12):
        auth = util.get_reddit_auth()
        self.reddit = praw.Reddit(**auth)

        # start yesterday
        self.hours = hours
        self.default_start = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        # end now
        self.default_end = datetime.datetime.utcnow()

    def get_num_submissions_per_hour(self, subreddit, hours=None, end=None):

        '''
        Get number of submissions to subreddit in time range.

        Returns:
            Tuple: (Number of submissions per hour averaged over hours, Num Submissions in Last Hour)
        '''
        if hours is None:
            start = self.default_start
        else:
            start = self.default_end - datetime.timedelta(hours=hours)
        if end is None:
            end = self.default_end
        start_one = end - datetime.timedelta(hours=1)
        submissions_x_h = [s for s in self.reddit.subreddit(subreddit).submissions(start.timestamp(), end.timestamp())]
        num_submission_x_h = len(submissions_x_h)
        num_submission_one_h = len([s for s in submissions_x_h if s.created_utc > start_one.timestamp()])
        num_per_h_in_x_h = float(num_submission_x_h)/np.abs(int(end.timestamp()) - int(start.timestamp()))*HOUR_IN_SECONDS
        return (num_per_h_in_x_h, num_submission_one_h)

    def get_num_subscribers(self, subreddit):
        return (self.reddit.subreddit(subreddit).subscribers)

    def get_num_comments_per_hour(self, subreddit, hours=None):
        if hours is None:
            start = self.default_start
        else:
            start = self.default_end - datetime.timedelta(hours=hours)
        start_one = self.default_end - datetime.timedelta(hours=1)
        comm = self.reddit.subreddit(subreddit).comments(limit=1024)
        cntagg = 0
        cntone = 0
        exit_by_break = False
        for c in comm:
            if c.created_utc > self.default_end.timestamp():
                continue
            cntagg += 1
            if c.created_utc > int(start_one.timestamp()):
                cntone += 1
            if c.created_utc < int(start.timestamp()):
                exit_by_break = True
                break
            last_created = c.created_utc

        if cntagg <= 1:
            comments_per_sec_in_x_h = 0.
        else:
            if exit_by_break:
                # if we exit by break we have seen all comments in the given interval
                # => divide by length of interval
                comments_per_sec_in_x_h = float(cntagg)/np.abs(int(self.default_end.timestamp()) - int(start.timestamp()))
            else:
                # if we dont exit by break we have only seen the first 1000 comments
                # => extrapolate by dividing with the shorter interval
                comments_per_sec_in_x_h = float(cntagg)/np.abs(int(self.default_end.timestamp()) - int(last_created))
        if cntone <= 1:
            comments_per_sec_in_1_h = 0.
        else:
            comments_per_sec_in_1_h = float(cntone)/HOUR_IN_SECONDS
        return (comments_per_sec_in_x_h*HOUR_IN_SECONDS, comments_per_sec_in_1_h*HOUR_IN_SECONDS)

    def get_mentions(self, coin_name_array, hours=None, include_submissions=False):
        """
        counts how often words from coin_name_tuple were mentioned in subreddits from subreddit list
        since start
        """
        if hours is None:
            start = self.default_start
        else:
            start = self.default_end - datetime.timedelta(hours=hours)
        hour_ago = self.default_end - datetime.timedelta(hours=1)
        count_list = len(coin_name_array) * [0.]
        first_hour_list = len(coin_name_array) * [0.]
        regex_list = []
        for coin_name_tuple in coin_name_array:
            pattern = r"\b|\b".join(coin_name_tuple)
            pattern = r"\b"+pattern+r"\b"
            regex_list.append(re.compile(pattern, re.I|re.UNICODE))
        comm_created = float('inf')
        submission_created = float('inf')
        for sub in GENERAL_SUBS:
            comments = self.reddit.subreddit(sub).comments(limit=1024)
            # search in comments
            for comm in comments:
                if int(comm.created_utc) < int(start.timestamp()):
                    break
                comm_created = min(comm_created, comm.created_utc)
                for i, regex in enumerate(regex_list):
                    if not re.search(regex, comm.body) is None:
                        count_list[i] += 1
                        if int(comm.created) < int(hour_ago.timestamp()):
                            first_hour_list[i] += 1
            # search in submissions
            if include_submissions:
                for submission in self.reddit.subreddit(sub).new():
                    if int(submission.created_utc) < int(start.timestamp()):
                        break
                    submission_created = min(submission_created, submission.created_utc)
                    for i, regex in enumerate(regex_list):
                        if not re.search(regex, submission.title) is None:
                            count_list[i] += 1
                            if int(submission.created) < int(hour_ago.timestamp()):
                                first_hour_list[i] += 1
        interval_length = self.default_end.timestamp() - min(comm_created, submission_created)
        count_list = np.array(count_list) / (interval_length / HOUR_IN_SECONDS)
        return (count_list, first_hour_list)

    def compile_dict(self, subreddit, hours=None):
        if hours is None:
            hours = self.hours
        d = {}
        comment_rates =  self.get_num_comments_per_hour(subreddit, hours=hours)
        submission_rates = self.get_num_submissions_per_hour(subreddit, hours=hours)
        d["time"] = datetime.datetime.fromtimestamp(int(self.default_end.timestamp()))
        d["hours"] = hours
        d["subreddit"] = subreddit
        d["subscribers"] = self.get_num_subscribers(subreddit)
        d["submission_rate"] = submission_rates[0]
        d["comment_rate"] = comment_rates[0]
        d["submission_rate_1h"] = submission_rates[1]
        d["comment_rate_1h"] = comment_rates[1]
        return d

    def find_subreddits(self, coin_name_list):
        """
        tries to find the corresponding subreddits for a list of crypto coin names
        """
        subreddit_names = []
        keywords = ["crypto", "blockchain", "decentral", "currency", "coin", "trading"]
        pattern = "|".join(keywords)
        regex = re.compile(pattern, re.I|re.UNICODE)
        for name in coin_name_list:
            sub_found = True
            try:
                sub = self.reddit.subreddit(name)
                public_description = str(sub.public_description)
                description = str(sub.description)
            except:
                sub_found = False

            if not sub_found or (re.search(regex, description) == None and re.search(regex, public_description) == None):
                # no keyword appears in subreddit description
                # it's probably not crypto coin related
                log.info("Sub {} not found or is not crypto related.".format(name))
                # finding alternatives
                # works poorly so its deactivated
                # print("Alternatives:")
                candidates = self.reddit.subreddits.search(name + " coin")
                found_alt = False
                for candidate in candidates:
                    if candidate.display_name.lower() in GENERAL_SUBS:
                        continue
                    public_description = str(candidate.public_description)
                    description = str(candidate.description)
                    if not (re.search(regex, description) == None and re.search(regex, public_description) == None):
                        # print(candidate.display_name)
                        subreddit_names.append(name)
                        found_alt = True
                        break
                if not found_alt:
                    subreddit_names.append("")
            else:
                subreddit_names.append(name)
        return subreddit_names

    def find_by_symbols(self, path):
        """
        Helps finding subreddits for coins which cannot be found with the find_subreddits command.
        path: Path to file with a list of coin SYMBOLS (i.e. BTC, ETH, ...)
        """
        a = util.read_csv(path)
        symbols = [s[0] for s in a]
        known_coin_name_array = util.read_subs_from_file(general["subreddit_file"])
        not_found, found = util.known_subs_for_symbols(known_coin_name_array, symbols)
        cap = CoinCap()
        coins = cap.get_coin_aliases(1000)
        coin_name_array = []
        # try finding remaining coins
        for coin in coins:
            if coin[-1] in not_found:
                coin_name_array.append(coin)
        if(len(symbols) != len(coin_name_array)):
            log.info("No coin data for {} coins.".format(len(symbols) - len(coin_name_array)))
        coin_name_array = sorted(coin_name_array, key=lambda c: c[-1])
        for coin_tuple in coin_name_array:
            coin_tuple.append("".join(x for x in coin_tuple[0] if x.isalnum()))
        subreddit_list = self.find_subreddits([name[-1] for name in coin_name_array])
        for i,coin in enumerate(coin_name_array):
            coin[-1] = subreddit_list[i]
        return coin_name_array, found
