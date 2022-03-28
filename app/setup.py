from fastapi import FastAPI
from starlette.responses import RedirectResponse
from .api.routes import scrapper_router
from .config import settings


def create_app() -> FastAPI:
    """Create the application instance"""
    app = FastAPI(title=settings.SERVER_NAME)
    app.include_router(scrapper_router)

    @app.get("/")
    async def docs() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    @app.get("/routes")
    async def routes():
        return {
            "routes to visit": [
                {"path": route.path, "name": route.name} for route in app.routes
            ]
        }

    return app
