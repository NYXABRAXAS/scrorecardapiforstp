from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["UI"])


@router.get("/", include_in_schema=False)
def scorecard_console() -> FileResponse:
    return FileResponse(Path("app/static/index.html"))


@router.get("/generate-scorecard", include_in_schema=False)
def generate_scorecard_console() -> FileResponse:
    return FileResponse(Path("app/static/index.html"))


@router.get("/simulate-scorecard", include_in_schema=False)
def simulate_scorecard_console() -> FileResponse:
    return FileResponse(Path("app/static/index.html"))
