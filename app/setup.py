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
        openapi_url=settings.OPENAPI_URL,
        swagger_ui_oauth2_redirect_url=settings.SWAGGER_UI_OAUTH2_REDIRECT_URL,
        docs_url=settings.DOCS_URL,
        redoc_url=None,
    )
    app.include_router(scrapper_router)
    setup_logging()
    return app
