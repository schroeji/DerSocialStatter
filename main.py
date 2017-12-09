from database import DatabaseConnection
from reddit import RedditStats

subreddit_list = ["dogecoin", "litecoin", "monero", "nem", "potcoin", "substratumnetwork"]

def main():
    stat = RedditStats()
    db = DatabaseConnection("postgres", "postgres")
    item_list = []
    for subreddit in subreddit_list:
        item_list.append(stat.compile_dict(subreddit))
    db.insert_list(item_list)
    db.close()

if __name__ == "__main__":
    main()
