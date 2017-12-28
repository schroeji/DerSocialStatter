import json
import logging

from settings import general


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

def export_to_csv(path, data_array, append=False):
    string = "\n".join([",".join([str(e) for e in tup]) for tup in data_array])
    if append:
        f = open(path, "a")
        f.write("\n")
    else:
        f = open(path, "w")
    f.write(string)
    f.close()

def read_csv(path):
    f = open(path, "r")
    inp = f.read()
    f.close()
    rows = inp.split("\n")
    result = []
    for r in rows:
        result.append(r.split(","))
    return result[:-1]

def read_subs_from_file(path):
    return read_csv(path)

def sort_by_symbol(coin_name_array):
    return sorted(coin_name_array, key=lambda c: c[-2])

def merge_coin_arrays(arr1, arr2):
    result = []
    for a1 in arr1:
        result.append(a1)
        for a2 in arr2:
            if a1[-2] == a2[-2] and a1 != a2:
                log.info("Conflicting entries:")
                log.info(a1)
                log.info(a2)

    for a2 in arr2:
        if not a2[-2] in [a1[-2] for a1 in arr1]:
            result.append(a2)
    return result
