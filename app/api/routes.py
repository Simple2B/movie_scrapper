import base64
import requests
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .actions import write_link
from ..logging import logger


scrapper_router = APIRouter(prefix="/scrap")


@scrapper_router.get("/")
async def routes(request: Request):
    """Return of the root link of the api"""
    return JSONResponse(
        content={
            "routes to visit": [
                {"path": route.path, "name": route.name}
                for route in request.app.routes
                if "/scrap" in route.path
            ]
        }
    )


@scrapper_router.post("/generalist/{target_link_encoded}")
def input_movies_url(
    target_link_encoded: str,
    q_string: Optional[str] = None,
    q_imdb: Optional[str] = None,
):

    movie_name = q_string if q_string else "undefined"
    logger.info(f"Movie name: {movie_name}")

    imdb = q_imdb if q_imdb else "undefined"
    logger.info(f"IMDB: {imdb}")

    try:
        target_link_decoded = base64.b64decode(target_link_encoded).decode("utf-8")
        logger.info(f"Target link: {target_link_decoded}")
    except Exception as err:
        logger.warning(f"Target link decode error: {err}")
        return JSONResponse(content={"DecodedError": str(err)}, status_code=400)

    try:
        target_link_response = requests.head(target_link_decoded)
    except requests.ConnectionError as err:
        logger.warning(f"Target link connection error: {err}")
        return JSONResponse(content={"ConnectionError": str(err)}, status_code=400)

    if target_link_response.status_code == 200:
        logger.info(f"Target link is valid: {target_link_decoded}")
        return JSONResponse(
            content={
                "list_of_links": write_link(target_link_decoded),
                "movie_name": movie_name,
                "imdb": imdb,
            },
            status_code=200,
        )
    else:
        logger.warning(f"Target link is not valid: {target_link_decoded}")
        return JSONResponse(
            content={"UnexpectedLinkRequest": target_link_response.status_code},
            status_code=400,
        )
