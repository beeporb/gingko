"""Module containing pydantic models and associates types for the request and response forms issued
to extraction API routes."""

import pathlib
from typing import Literal

from pydantic import BaseModel

ExtractionType = Literal["tar", "zip", "directory"]


class Extraction(BaseModel):
    """Model representing an extraction that is waiting for processing in the system."""

    path: pathlib.PurePath
    type: ExtractionType
    size_on_disk: int
    files: int


class GetExtractionRequest(BaseModel):
    """Model for the GET /extraction request."""
    path: pathlib.PurePath | None = None
    type: ExtractionType | None = None


class GetExtractionResponse(BaseModel):
    """Model for the GET /extraction response."""
    extractions: list[Extraction]
