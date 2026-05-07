from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import health, rules, scorecard, ui
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Configurable STP scorecard engine for two wheeler loan LOS integrations.",
    )
    app.include_router(health.router)
    app.include_router(scorecard.router)
    app.include_router(rules.router)
    app.include_router(ui.router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    return app


app = create_app()
