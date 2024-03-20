"""Module containing functionality pertaining to tracking Extractions in Gingko, specifically
tracking whether extractions on disk have been seen before or not."""

import abc
import pathlib

import redis

from gingko.config import GINGKO_REDIS_HOST, GINGKO_REDIS_PORT
from gingko.server.extraction.model import Extraction, ExtractionType


class GingkoTrackingClient(abc.ABC):
    """Abstract class for a client that tracks the seen-status of different extractions on disk."""

    @abc.abstractmethod
    def get_tracked_extractions(self) -> list[Extraction]:
        """Get all extractions that have been seen by the system.

        Returns:
            list[Extraction]: List of extractions that have been seen by the system.
        """
        ...

    @abc.abstractmethod
    def check_path_tracked(self, path: pathlib.PurePath) -> bool:
        """Check if the provided PurePath has been seen before.

        Args:
            path (pathlib.PurePath): Path to check if it has been seen or not.

        Returns:
            bool: Whether or not the path has been seen by the system or not.
        """
        ...

    @abc.abstractmethod
    def remove_tracking_for_extraction(self, extraction: Extraction):
        """Remove a specific extraction from the tracker.

        Args:
            extraction (Extraction): Extraction to remove from the tracker.
        """
        ...

    @abc.abstractmethod
    def get_tracked_extraction_data_by_path(self, path: pathlib.PurePath) -> Extraction:
        """Get a specific extraction by path from the tracker.

        Args:
            path (pathlib.PurePath): Path to get extraction for.

        Returns:
            Extraction: Extraction that corresponds to provided path.
        """
        ...

    @abc.abstractmethod
    def get_tracked_extraction_data_by_type(self, type: ExtractionType) -> list[Extraction]:
        """Get a list of extractions that match a specific type.

        Args:
            type (ExtractionType): ExtractionType, such as tar, directory etc.

        Returns:
            list[Extraction]: List of extractions that match this type.
        """
        ...

    @abc.abstractmethod
    def add_tracking_for_extraction(self, extraction: Extraction) -> None:
        """Add tracking for an extraction to the tracker.

        Args:
            extraction (Extraction): Extraction to add to the tracker.
        """
        ...


class RedisGingkoTrackingClient(GingkoTrackingClient):
    """Implementation of the GingkoTrackingClient abstract class that uses Redis to store the
    tracking information."""

    _REDIS_TRACKING_KEYS_KEY = "gingko-tracking-keys"
    _REDIS_TRACKING_DATA_PREFIX = "gingko-tracking::"

    def __init__(self, host: str = GINGKO_REDIS_HOST, port: int = GINGKO_REDIS_PORT) -> None:
        """Constructor for the class.

        Args:
            host (str, optional): Hostname where Redis can be found. Defaults to GINGKO_REDIS_HOST.
            port (int, optional): Port that Reds is running on. Defaults to GINGKO_REDIS_PORT.
        """
        self.connection = redis.StrictRedis(host=host,
                                            port=port,
                                            decode_responses=True,
                                            charset="utf-8")

    def get_tracked_extractions(self) -> list[Extraction]:
        tracked_extraction_keys = self.connection.smembers(self._REDIS_TRACKING_KEYS_KEY)

        extractions: list[Extraction] = []

        for tracked_extraction_key in tracked_extraction_keys:

            raw = self.connection.hgetall(
                f"{self._REDIS_TRACKING_DATA_PREFIX}{tracked_extraction_key}")

            extraction = Extraction(**raw)

            extractions.append(extraction)

        return extractions

    def check_path_tracked(self, path: pathlib.PurePath) -> bool:
        return bool(self.connection.sismember(self._REDIS_TRACKING_KEYS_KEY, str(path)))

    def get_tracked_extraction_data_by_path(self, path: pathlib.PurePath) -> Extraction | None:
        if self.check_path_tracked(path):
            raw = self.connection.hgetall(f"{self._REDIS_TRACKING_DATA_PREFIX}{path}")
            return Extraction(**raw)
        else:
            return None

    def get_tracked_extraction_data_by_type(self,
                                            extraction_type: ExtractionType) -> list[Extraction]:

        tracked_extractions = self.get_tracked_extractions()
        return [
            extraction for extraction in tracked_extractions if extraction.type == extraction_type
        ]

    def remove_tracking_for_extraction(self, extraction: Extraction):
        extraction_path = extraction.path

        if not self.check_path_tracked(extraction_path):
            return

        tracked_extracton_key = f"{self._REDIS_TRACKING_DATA_PREFIX}{str(extraction_path)}"

        self.connection.delete(tracked_extracton_key)
        self.connection.srem(self._REDIS_TRACKING_KEYS_KEY, str(extraction_path))

    def add_tracking_for_extraction(self, extraction: Extraction) -> None:

        extraction_path = extraction.path
        tracked_extraction_key = f"{self._REDIS_TRACKING_DATA_PREFIX}{str(extraction_path)}"

        if self.check_path_tracked(extraction_path):
            raise Exception("already tracked (make an error for this)")

        self.connection.sadd(self._REDIS_TRACKING_KEYS_KEY, str(extraction_path))
        self.connection.hset(tracked_extraction_key, mapping=dict(extraction))
