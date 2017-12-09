import psycopg2

class DatabaseConnection:
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
        self.cur.execute("SELECT * FROM data;")
        return self.cur.fetchall()

    def close(self):
        """
        close the database connection
        """
        self.conn.commit()
        self.cur.close()
        self.conn.close()