"""Module containing the API router that handles extractions."""

from fastapi import APIRouter

from gingko.server.extraction.model import GetExtractionRequest, GetExtractionResponse, Extraction
from gingko.server.extraction.tracking import RedisGingkoTrackingClient

extraction_router = APIRouter(prefix="/extraction")


@extraction_router.get("/")
def get_extraction(req: GetExtractionRequest | None = None) -> GetExtractionResponse:
    """.

    Args:
        req (GetExtractionRequest | None, optional): Request body, used for filtering. Defaults to 
        None.

    Returns:
        GetExtractionResponse: Request response, contains extractions.
    """

    tracking_client = RedisGingkoTrackingClient()

    extractions: list[Extraction] = []

    if not req:

        extractions = tracking_client.get_tracked_extractions()

    elif req.path:

        extractions = [tracking_client.get_tracked_extraction_data_by_path(req.path)]

    elif req.type:

        extractions = tracking_client.get_tracked_extraction_data_by_type(req.type)

    return GetExtractionResponse(extractions=extractions)
