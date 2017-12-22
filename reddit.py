import praw
import datetime
import numpy as np
import re
import util
# add logging
HOUR_IN_SECONDS = 3600

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
        for c in comm:
            cntagg += 1
            if c.created_utc > int(start_one.timestamp()):
                cntone += 1
            if c.created_utc < int(start.timestamp()):
                break
            last_created = c.created_utc
        if cntagg <= 1:
            comments_per_sec_in_x_h = 0.
        else:
            comments_per_sec_in_x_h = float(cntagg)/np.abs(int(self.default_end.timestamp()) - int(last_created))
        if cntone <= 1:
            comments_per_sec_in_1_h = 0.
        else:
            comments_per_sec_in_1_h = float(cntone)/HOUR_IN_SECONDS
        return (comments_per_sec_in_x_h*HOUR_IN_SECONDS, comments_per_sec_in_1_h*HOUR_IN_SECONDS)

    def get_mentions(self, coin_name_array, subreddit_list, hours=None, include_submissions=False):
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
        for sub in subreddit_list:
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
        # ignore_subs = ["cryptocurrency", "cryptotrading", "cryptotrade", "cryptomarkets", "cryptowallstreet"]
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
                # print("Sub {} does not exist".format(name))

            if not sub_found or (re.search(regex, description) == None and re.search(regex, public_description) == None):
                # no keyword appears in subreddit description
                # it's probably not crypto coin related
                print("Sub {} not found or is not crypto related.".format(name))
                # finding alternatives
                # works poorly so its deactivated
                # print("Alternatives:")
                # candidates = self.reddit.subreddits.search(name + " coin")
                # for candidate in candidates:
                #     if candidate.display_name.lower() in ignore_subs:
                #         continue
                #     public_description = str(candidate.public_description)
                #     description = str(candidate.description)
                #     if not (re.search(regex, description) == None and re.search(regex, public_description) == None):
                #         print(candidate.display_name)
                        # subreddit_names.append(name)
            else:
                subreddit_names.append(name)
        return subreddit_names
