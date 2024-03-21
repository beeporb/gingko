"""Module containing functionality for configuring various bits of Gingko with environment
variables."""

import os
import pathlib

GINGKO_INPUT_DIR = pathlib.Path(os.getenv("GINGKO_INPUT_DIR", "/mnt/data"))
GINGKO_LOGGING_DIR = pathlib.Path(os.getenv("GINGKO_LOGGING_DIR", "/var/log/gingko"))

GINGKO_REDIS_HOST = os.getenv("GINGKO_REDIS_HOST", "redis")
GINGKO_REDIS_PORT = os.getenv("GINGKO_REDIS_PORT", "6379")
GINGKO_REDIS = os.getenv("GINGKO_REDIS", f"redis://{GINGKO_REDIS_HOST}:{GINGKO_REDIS_PORT}")
