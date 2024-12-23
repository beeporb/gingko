"""Module containing functionality for configuring various bits of Gingko with environment
variables."""

import os
import pathlib

GINGKO_INPUT_DIR = pathlib.Path(os.getenv("GINGKO_INPUT_DIR", "/mnt/data"))
GINGKO_LOGGING_DIR = pathlib.Path(os.getenv("GINGKO_LOGGING_DIR", "/var/log/gingko"))

GINGKO_REDIS_HOST = os.getenv("GINGKO_REDIS_HOST", "redis")
GINGKO_REDIS_PORT = os.getenv("GINGKO_REDIS_PORT", "6379")
GINGKO_REDIS = os.getenv("GINGKO_REDIS", f"redis://{GINGKO_REDIS_HOST}:{GINGKO_REDIS_PORT}")

GINGKO_ELASTIC_HOST = os.getenv("GINGKO_ELASTIC_HOST", "elastic")
GINGKO_ELASTIC_PORT = os.getenv("GINGKO_ELASTIC_PORT", "9200")
GINGKO_ELASTIC = os.getenv("GINGKO_ELASTIC", f"http://{GINGKO_ELASTIC_HOST}:{GINGKO_ELASTIC_PORT}")
GINGKO_ELASTIC_FILE_METADATA_INDEX = os.getenv("GINGKO_ELASTIC_FILE_METADATA_INDEX",
                                               "gingko-filestore")
