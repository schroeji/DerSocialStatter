import psycopg2

class DatabaseConnection(object):
    """
    Class for PostgreSQL connections using psycopg2
    http://initd.org/psycopg/docs/usage.html
    """

    def __init__(self, dbname, user):
        try:
            self.conn = psycopg2.connect("dbname={} user={}".format(dbname, user))
            self.cur = self.conn.cursor()
            if (not self.table_exists()):
                self.create_table()
        except:
            print("Could not connect to databse!")

    def table_exists(self):
        self.cur.execute("SELECT * FROM information_schema.tables where table_name=%s ;", ("data",))
        return self.cur.rowcount > 0

    def create_table(self):
        """
        create the main data table
        format: |id|start_time|end_time|subreddit|subscribers|submissions|comment_rate|
        """
        self.cur.execute("CREATE TABLE data (id serial PRIMARY KEY, start_time timestamp,"
                         "end_time timestamp, subreddit varchar, subscribers int,"
                         "submissions int, comment_rate real);")
        self.conn.commit()
        print("Created data table.")

    def delete_table(self):
        """
        drop the data table
        """
        self.cur.execute("DROP TABLE data;")
        self.conn.commit()
        print("Dropped data table.")

    def insert(self, data_dict):
        """
        insert a data item into the table
        """
        self.cur.execute("INSERT INTO data (start_time, end_time, subreddit, subscribers, submissions, comment_rate)"
                         "VALUES (%s, %s, %s, %s, %s, %s);",
                         (data_dict["start_time"], data_dict["end_time"], data_dict["subreddit"],
                          data_dict["subscribers"], data_dict["submissions"], data_dict["comment_rate"]))
        self.conn.commit()

    def insert_list(self, d_list):
        """
        insert a list of data items into the table
        """
        for data_dict in d_list:
            self.cur.execute("INSERT INTO data (start_time, end_time, subreddit, subscribers, submissions, comment_rate)"
                             "VALUES (%s, %s, %s, %s, %s, %s);",
                             (data_dict["start_time"], data_dict["end_time"], data_dict["subreddit"],
                              data_dict["subscribers"], data_dict["submissions"], data_dict["comment_rate"]))
        self.conn.commit()

    def get_all_rows(self):
        """
        return a list of all rows in the data table
        """
        self.cur.execute("SELECT * FROM data;")
        return self.cur.fetchall()

    def close(self):
        """
        close the database connection
        """
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def get_all_subreddits(self):
        # TODO: method that returns only subreddits that have data in the last day
        """
        returns a list of all subreddits in the database
        """
        self.cur.execute("SELECT DISTINCT subreddit FROM data;")
        return [x[0] for x in self.cur.fetchall()]

    def get_metrics_for_subreddit(self, subreddit, timeinterval=None):
        # TODO custom timeinterval, minimum time distance
        """
        gets two last values from subscribers, submissions and comment_rate

        Args:
            subreddit: string
            timeinterval: tuple of timestamp or None, if none take last and second to last timestamp

        Returns:
            List of Tuples containing metrics from subreddit, time is decreasing
        """
        if timeinterval is None:
            querystr = "SELECT subscribers, submissions, comment_rate FROM data WHERE subreddit=%s \
                    AND end_time in (SELECT DISTINCT end_time FROM data ORDER BY end_time DESC LIMIT 2) \
                    ORDER BY end_time DESC LIMIT 2"
        self.cur.execute(querystr, (subreddit,))
        return self.cur.fetchall()
