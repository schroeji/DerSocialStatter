import datetime

import numpy as np
import psycopg2

from util import setup_logger

log = setup_logger(__name__)

class DatabaseConnection(object):
    """
    Class for PostgreSQL connections using psycopg2
    http://initd.org/psycopg/docs/usage.html
    """

    def __init__(self, dbname, user, password, host="localhost"):
        try:
            self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
            self.cur = self.conn.cursor()
        except:
            log.error("Could not connect to databse!")
            return
        if (not self.data_table_exists()):
            self.create_data_table()
        if (not self.price_table_exists()):
            self.create_price_table()

    def close(self):
        """
        close the database connection
        """
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    # ------------ price table ------------

    def price_table_exists(self):
        self.cur.execute("SELECT * FROM information_schema.tables where table_name=%s ;", ("price",))
        return self.cur.rowcount > 0

    def create_price_table(self):
        """
        create the price data table
        format: |id|time|coin_id|coin_name|symbol|subreddit|price|percent_change_1h|percent_change_24h|
        """
        self.cur.execute("CREATE TABLE price (id serial PRIMARY KEY, time timestamp, \
                         coin_id varchar, coin_name varchar, symbol varchar, subreddit varchar, \
                         price real, percent_change_1h real, percent_change_24h real);")
        self.conn.commit()
        log.info("Created price table.")

    def delete_price_table(self):
        """
        drop the data table
        """
        self.cur.execute("DROP TABLE data;")
        self.conn.commit()
        log.info("Dropped data table.")

    def insert_price(self, price_data_dict):
        """
        insert a price item into the table
        """
        self.cur.execute("INSERT INTO price (time, coin_id, coin_name, symbol, subreddit, price, percent_change_1h,  percent_change_24h)"
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                         (price_data_dict["time"], price_data_dict["coin_id"], price_data_dict["coin_name"],
                          price_data_dict["symbol"], price_data_dict["subreddit"], price_data_dict["price"],
                          price_data_dict["percent_change_1h"], price_data_dict["percent_change_24h"])
        )
        self.conn.commit()


    def get_interpolated_price_data(self, subreddit, timestamp):
        """
        Returns price, percent_change_1h, percent_change_24h
        Created by linear interpolation using the two nearest datapoints.
        """
        querystr = "SELECT time, price, percent_change_1h, percent_change_24h FROM price WHERE subreddit=%s \
                AND time > %s ORDER BY time ASC LIMIT 1"
        self.cur.execute(querystr, (subreddit, timestamp))
        next_newer = self.cur.fetchone()
        querystr = "SELECT time, price, percent_change_1h, percent_change_24h FROM price WHERE subreddit=%s \
                AND time < %s ORDER BY time DESC LIMIT 1"
        self.cur.execute(querystr, (subreddit, timestamp))
        next_older = self.cur.fetchone()
        if next_newer == None and next_older == None:  # if no newer data exists return the latest data
            log.warning("No match for %s" % (subreddit))
            return
        elif next_newer == None:
            return next_older[1:]
        elif next_older == None:  # if no older data exists raise error
            raise ValueError("Cannot interpolate for given timestamp, subreddit: {} {}".format(timestamp, subreddit))
        # weighted interpolation
        interval = next_newer[0] - next_older[0]
        weight_newer = (next_newer[0] - timestamp) / interval
        weight_older = (timestamp - next_older[0]) / interval
        return weight_newer*np.array(next_newer[1:]) + weight_older*np.array(next_older[1:])


    def get_all_price_data_in_interval(self, start, end):
        """
        Returns all data points for all subreddits in the given interval (newest first).
        """
        querystr = "SELECT subreddit, price, percent_change_1h, percent_change_24h \
                FROM price WHERE time > %s AND time < %s ORDER BY time DESC"
        self.cur.execute(querystr, (start, end))
        return self.cur.fetchall()

    # ------------ data table ------------

    def data_table_exists(self):
        self.cur.execute("SELECT * FROM information_schema.tables where table_name=%s ;", ("data",))
        return self.cur.rowcount > 0

    def create_data_table(self):
        """
        create the main data table
        format: |id|time|hours|subreddit|subscribers|submission_rate|comment_rate|mention_rate|submission_rate_1h|comment_rate_1h|mention_rate_1h|
        """
        self.cur.execute("CREATE TABLE data (id serial PRIMARY KEY, time timestamp,"
                         "hours int, subreddit varchar, subscribers int,"
                         "submission_rate real, comment_rate real, mention_rate real,"
                         "submission_rate_1h real, comment_rate_1h real, mention_rate_1h real);")
        self.conn.commit()
        log.info("Created data table.")

    def delete_data_table(self):
        """
        drop the data table
        """
        self.cur.execute("DROP TABLE data;")
        self.conn.commit()
        log.info("Dropped data table.")

    def insert_data(self, data_dict):
        """
        insert a data item into the table
        """
        self.cur.execute("INSERT INTO data (time, hours, subreddit, subscribers, submission_rate, comment_rate, mention_rate, submission_rate_1h, comment_rate_1h, mention_rate_1h)"
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                         (data_dict["time"], data_dict["hours"], data_dict["subreddit"],
                          data_dict["subscribers"], data_dict["submission_rate"], data_dict["comment_rate"], data_dict["mention_rate"],
                          data_dict["submission_rate_1h"], data_dict["comment_rate_1h"], data_dict["mention_rate_1h"]))
        self.conn.commit()

    # ------------ data table queries------------

    def get_all_subreddits(self):
        # TODO: method that returns only subreddits that have data in the last day
        """
        returns a list of all subreddits in the database
        """
        self.cur.execute("SELECT DISTINCT subreddit FROM data;")
        return [x[0] for x in self.cur.fetchall()]

    def get_rows_for_subreddit(self, subreddit, start=None, end=None):
        if start is None: start = datetime.datetime.fromtimestamp(0)
        if end is None: end = datetime.datetime.utcnow()
        querystr = "SELECT start_time, end_time, subscribers, submission_rate, comment_rate, mention_rate, \
            submission_rate_1h, comment_rate_1h, mention_rate_1h FROM data WHERE subreddit=%s \
            AND end_time < %s AND start_time > %s ORDER BY end_time DESC"
        self.cur.execute(querystr, (subreddit, end, start))
        return self.cur.fetchall()

    def get_metrics_for_subreddit(self, subreddit, start=None, end=None):
        # TODO custom timeinterval, minimum time distance
        """
        gets all tuples of subscribers, submission_rate and comment_rate in the given time interval

        Args:
            subreddit: string
            start: start-timestamp
            end: end-timestamp

        Returns:
            List of Tuples containing metrics from subreddit, time is decreasing
            If only one of start and end is given the other one is not constrained.
            If neither is given returns the metrics for the last two rows in the table.
        """
        if start is None and end is None:
            querystr = "SELECT subscribers, submission_rate, comment_rate, mention_rate, \
                    submission_rate_1h, comment_rate_1h, mention_rate_1h FROM data WHERE subreddit=%s \
                    AND time in (SELECT DISTINCT time FROM data ORDER BY time DESC LIMIT 2) \
                    ORDER BY time DESC LIMIT 2"
            self.cur.execute(querystr, (subreddit,))
        else:
            if start is None: start = datetime.datetime.fromtimestamp(0)
            if end is None: end = datetime.datetime.utcnow()
            querystr = "SELECT subscribers, submission_rate, comment_rate, mention_rate, \
                    submission_rate_1h, comment_rate_1h, mention_rate_1h FROM data WHERE subreddit=%s \
                    AND time < %s AND time > %s ORDER BY time DESC"
            self.cur.execute(querystr, (subreddit, end, start))
        return self.cur.fetchall()

    def get_data_for_subreddit(self, subreddit, time):
        """
        Returns the most recent (i.e. the next older ) metrics tuple
        for the subreddit and timestamp.
        """
        querystr = "SELECT subscribers, submission_rate, comment_rate, mention_rate, \
                submission_rate_1h, comment_rate_1h, mention_rate_1h FROM data WHERE subreddit=%s \
                AND time < %s ORDER BY time DESC"
        self.cur.execute(querystr, (subreddit, time))
        next_older = self.cur.fetchone()
        if next_older is None:
            raise ValueError("Cannot get data for given timestamp, subreddit: {} {}".format(timestamp, subreddit))
        return next_older

    def get_all_data_in_interval(self, start, end):
        """
        Returns all data points for all subreddits in the given interval
        """
        querystr = "SELECT subreddit, subscribers, submission_rate, comment_rate, mention_rate, \
                submission_rate_1h, comment_rate_1h, mention_rate_1h FROM data WHERE \
                time > %s AND time < %s ORDER BY time DESC"
        self.cur.execute(querystr, (start, end))
        return self.cur.fetchall()

    def get_interpolated_data(self, subreddit, timestamp):
        """
        Returns a metrics tuple for the subreddit for the given timestamp.
        Created by linear intrpolation using the two nearest datapoints.
        """
        querystr = "SELECT time, subscribers, submission_rate, comment_rate, mention_rate, \
                submission_rate_1h, comment_rate_1h, mention_rate_1h FROM data WHERE subreddit=%s \
                AND time > %s ORDER BY time ASC LIMIT 1"
        self.cur.execute(querystr, (subreddit, timestamp))
        next_newer = self.cur.fetchone()
        querystr = "SELECT time, subscribers, submission_rate, comment_rate, mention_rate, \
                submission_rate_1h, comment_rate_1h, mention_rate_1h FROM data WHERE subreddit=%s \
                AND time < %s ORDER BY time DESC LIMIT 1"
        self.cur.execute(querystr, (subreddit, timestamp))
        next_older = self.cur.fetchone()

        if next_newer is None and next_older is None:  # if no newer data exists return the latest data
            log.warning("No match for %s" % (subreddit))
            return []
        elif next_newer is None:  # if no newer data exists return the latest data
            return next_older[1:]
        elif next_older is None:  # if no older data exists raise error
            raise ValueError("Cannot interpolate for given timestamp, subreddit: {} {}".format(timestamp, subreddit))
        if next_newer[0] - next_older[0] > datetime.timedelta(hours=3):
            log.warning("Difference of timestamps while interpolating %s is %s" % (subreddit, next_newer[0] - next_older[0]))
        # weighted interpolation
        interval = next_newer[0] - next_older[0]
        weight_newer = (next_newer[0] - timestamp) / interval
        weight_older = (timestamp - next_older[0]) / interval
        return weight_newer*np.array(next_newer[1:]) + weight_older*np.array(next_older[1:])

    def get_subreddits_with_data(self, timestamp):
        """
        Gets all subreddits that have datapoints before a given datapoint
        """
        querystr = "SELECT DISTINCT subreddit FROM data WHERE time < %s"
        self.cur.execute(querystr, (timestamp,))
        return [i[0] for i in self.cur.fetchall()]
