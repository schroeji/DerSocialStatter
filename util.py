from settings import general
import logging
import json

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Setups logger and logfile.

    :rtype: Logger
    :param name: logger name.
    :param log_file: log file name.
    :param level: log level.
    :return: logger
    """
    if log_file is None:
        log_file = general['log_file']

    logger = logging.getLogger(name)
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    logging.basicConfig(level=level)
    return logger

log = setup_logger(__name__)


def get_reddit_auth():
    with open(general["auth_file"]) as f:
        auth = json.load(f)
    return auth['reddit']

def get_postgres_auth():
    with open(general["auth_file"]) as f:
        auth = json.load(f)
    return auth['postgres']

def write_subs_to_file(path, subreddit_list):
    export_to_csv(path, subreddit_list)

def export_to_csv(path, data_array):
    string = "\n".join([",".join([str(e) for e in tup]) for tup in data_array])
    f = open(path, "w")
    f.write(string)
    f.close()

def read_subs_from_file(path):
    f = open(path, "r")
    inp = f.read()
    f.close()
    rows = inp.split("\n")
    result = []
    for r in rows:
        result.append(r.split(","))
    return result[:-1]
