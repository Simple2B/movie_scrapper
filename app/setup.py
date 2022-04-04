from fastapi import FastAPI
from app.config import settings
from app.logging import setup_logging
from app.api.routes import scrapper_router


def create_app() -> FastAPI:
    """Create the application instance"""
    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        openapi_prefix=settings.OPENAPI_PREFIX,
    )
    app.include_router(scrapper_router)
    setup_logging()
    return app
