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
