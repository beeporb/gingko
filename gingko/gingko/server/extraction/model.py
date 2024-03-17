import pathlib
from typing import Literal

from pydantic import BaseModel

ExtractionType = Literal["tar", "zip", "directory"]


class Extraction(BaseModel):
    path: pathlib.PurePath
    type: ExtractionType
    size_on_disk: int
    files: int

    @property
    def processed(self) -> bool:
        ...


class GetExtractionRequest(BaseModel):
    path: pathlib.PurePath | None = None
    type: ExtractionType | None = None


class GetExtractionResponse(BaseModel):
    extractions: list[Extraction]
