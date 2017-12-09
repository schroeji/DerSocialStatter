import praw
import datetime
import numpy as np
import json
from database import DatabaseConnection

class RedditStats(object):
    def __init__(self):
        with open('auth.json') as f:
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

    def get_num_comments_per_hour(self, subreddit):
        comm = self.reddit.subreddit(subreddit).comments(limit=1024)

        cnt = 0
        for c in comm:
            if cnt == 0:
                first_timestamp = c.created

            t = datetime.datetime.fromtimestamp(int(c.created)).strftime('%Y-%m-%d %H:%M:%S')
            # print (t, c.created, self.default_start)

            current_timestamp = c.created
            cnt += 1
            if int(c.created) < int(self.default_start):
                # print (t, c.created, self.default_start)
                break

        if cnt <= 1:
            raise ValueError("Shit coin!, no comments in one fucking day!!!!!!!")


        comments_per_sec_in_on_day = cnt/np.abs((int(first_timestamp) - int(current_timestamp)))
        # print (cnt)
        # print (first_timestamp, current_timestamp)
        return comments_per_sec_in_on_day

    def compile_dict(self, subreddit):
        d = {}
        d["start_time"] = datetime.datetime.fromtimestamp(int(self.default_start))
        d["end_time"] = datetime.datetime.fromtimestamp(int(self.default_end))
        d["subreddit"] = subreddit
        d["subscribers"] = self.get_num_subscribers(subreddit)
        d["submissions"] = self.get_num_submissions(subreddit)
        d["comment_rate"] = self.get_num_comments_per_hour(subreddit)
        return d

# substratumnetwork
# 
def main():
    stat = RedditStats()
    db = DatabaseConnection("postgres", "postgres")
    item = stat.compile_dict("potcoin")
    db.insert(item)
    db.get_all_rows()
    db.close()
    # print (stat.get_num_submissions('potcoin'))
    # print (stat.get_num_comments_per_hour('potcoin'))

if __name__ == "__main__":
    main()
