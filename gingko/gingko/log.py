import logging
from logging.handlers import TimedRotatingFileHandler

from gingko.config import GINGKO_LOGGING_DIR

LOG_FILE = GINGKO_LOGGING_DIR / "gingko.log"
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"

FILE_HANDLER = TimedRotatingFileHandler(filename=LOG_FILE, when="d", interval=1, backupCount=30)
STREAM_HANDLER = logging.StreamHandler()


def init_logger() -> None:
    logging.basicConfig(handlers=[FILE_HANDLER, STREAM_HANDLER],
                        format=LOG_FORMAT,
                        level=logging.INFO)
