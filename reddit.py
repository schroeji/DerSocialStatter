import praw
import datetime
import numpy as np
import json
import re
import os

class RedditStats(object):

    def __init__(self):
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path + '/auth.json') as f:
            auth = json.load(f)
            f.close()

        self.reddit = praw.Reddit(**auth)

        # start yesterday
        self.default_start = datetime.datetime.now() - datetime.timedelta(1)
        self.default_start = self.default_start.strftime('%s')
        # end now
        self.default_end = datetime.datetime.now()
        self.default_end = self.default_end.strftime('%s')

    def get_num_submissions(self,
                            subreddit,
                            start=None,
                            end=None):

        '''
        Get number of submissions to subreddit in time range.
        '''
        if start is None:
            start = self.default_start
        if end is None:
            end = self.default_end
        return len([s for s in self.reddit.subreddit(subreddit).submissions(start, end)])

    def get_num_subscribers(self, subreddit):
        return (self.reddit.subreddit(subreddit).subscribers)

    def get_num_comments_per_hour(self, subreddit, start=None):
        if start is None:
            start = self.default_start
        comm = self.reddit.subreddit(subreddit).comments(limit=1024)
        cnt = 0
        for c in comm:
            cnt += 1
            if int(c.created) < int(start):
                break
        if cnt <= 1:
            return 0.
        # comments_per_sec_in_on_day = cnt/np.abs((int(first_timestamp) - int(current_timestamp)))
        comments_per_sec_in_on_day = float(cnt)/np.abs(int(self.default_end) - int(start))
        return comments_per_sec_in_on_day*3600

    def compile_dict(self, subreddit, start=None):
        if start is None:
            start = self.default_start
        d = {}
        d["start_time"] = datetime.datetime.fromtimestamp(int(start))
        d["end_time"] = datetime.datetime.fromtimestamp(int(self.default_end))
        d["subreddit"] = subreddit
        d["subscribers"] = self.get_num_subscribers(subreddit)
        d["submissions"] = self.get_num_submissions(subreddit, start=start)
        d["comment_rate"] = self.get_num_comments_per_hour(subreddit, start=start)
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
