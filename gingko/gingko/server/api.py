import fastapi

from gingko.server.extraction.router import extraction_router

api = fastapi.FastAPI()
api.include_router(extraction_router)
