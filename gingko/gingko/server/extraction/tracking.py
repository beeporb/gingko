import abc
import pathlib

import redis

from gingko.config import GINGKO_REDIS_HOST, GINGKO_REDIS_PORT
from gingko.server.extraction.model import Extraction, ExtractionType


class GingkoTrackingClient(abc.ABC):

    @abc.abstractmethod
    def get_tracked_extractions(self) -> list[Extraction]:
        ...

    @abc.abstractmethod
    def check_path_tracked(self, path: pathlib.PurePath) -> bool:
        ...

    @abc.abstractmethod
    def remove_tracking_for_extraction(self, extraction: Extraction) -> bool:
        ...

    @abc.abstractmethod
    def get_tracked_extraction_data_by_path(self, path: pathlib.PurePath) -> Extraction:
        ...


class RedisGingkoTrackingClient(GingkoTrackingClient):

    _REDIS_TRACKING_KEYS_KEY = "gingko-tracking-keys"
    _REDIS_TRACKING_DATA_PREFIX = "gingko-tracking::"

    def __init__(self, host: str = GINGKO_REDIS_HOST, port: int = GINGKO_REDIS_PORT) -> None:
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
