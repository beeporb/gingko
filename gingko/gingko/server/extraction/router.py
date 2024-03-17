from fastapi import APIRouter

from gingko.server.extraction.model import GetExtractionRequest, GetExtractionResponse, Extraction
from gingko.server.extraction.tracking import RedisGingkoTrackingClient

router = APIRouter()


@router.get("/extraction/")
def get_extraction(req: GetExtractionRequest) -> GetExtractionResponse:

    tracking_client = RedisGingkoTrackingClient()

    extractions: list[Extraction] = []

    match req:

        case req.path:

            extractions = tracking_client.get_tracked_extraction_data_by_path(req.path)

        case req.type:

            extractions = tracking_client.get_tracked_extraction_data_by_type(req.type)

        case _:

            extractions = tracking_client.get_tracked_extractions()

    return GetExtractionResponse(extractions=extractions)
