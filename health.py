from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.scorecard import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    database = "ok"
    redis_status = "disabled"
    details = {}
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        database = "error"
        details["database_error"] = str(exc)

    settings = get_settings()
    if settings.redis_url:
        try:
            Redis.from_url(settings.redis_url).ping()
            redis_status = "ok"
        except Exception as exc:
            redis_status = "error"
            details["redis_error"] = str(exc)
    status = "ok" if database == "ok" and redis_status in {"ok", "disabled"} else "degraded"
    return HealthResponse(status=status, database=database, redis=redis_status, details=details)

