"""Module containing the API router that handles extractions."""

from fastapi import APIRouter, HTTPException

from gingko.server.extraction.model import GetExtractionRequest, GetExtractionResponse, Extraction, DeleteExtractionRequest, DeleteExtractionResponse
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


@extraction_router.delete("/")
def delete_extraction(req: DeleteExtractionRequest) -> DeleteExtractionResponse:
    """Delete a specific extraction from the tracker.

    Args:
        req (DeleteExtractionRequest): Request body, used to select the extraction to delete.

    Raises:
        HTTPException: 404 raised in the event that the client tries to delete an extraction that
        doesn't exist.

    Returns:
        DeleteExtractionResponse: Request response, basically empty.
    """
    tracking_client = RedisGingkoTrackingClient()

    if not tracking_client.check_path_tracked(req.path):
        raise HTTPException(status_code=404, detail="No extraction tracked with that path.")

    extraction = tracking_client.get_tracked_extraction_data_by_path(req.path)

    tracking_client.remove_tracking_for_extraction(extraction)

    return {}
