from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from base64 import binascii
from selenium.common.exceptions import TimeoutException, WebDriverException
from pydantic.error_wrappers import ValidationError
from app.logging import logger
from app.api.schemas import Urls

from app.api.utils import decode_link, sort_urls


scrapper_router = APIRouter(prefix="/api")


@scrapper_router.post("/generalist/{target_link_encoded}", response_model=Urls)
async def input_movies_url(
    target_link_encoded: str,
) -> Urls:
    from app.api.scrapper import get_links

    try:
        url = decode_link(target_link_encoded)
        logger.info("Incoming URL detected: [{}].", url)
        data = Urls(target_url=url)
    except (binascii.Error, UnicodeDecodeError) as err:
        data = Urls(error=str(err))
        logger.error("Failed to decode incoming data [{}].", target_link_encoded)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=data.dict()
        )
    except ValidationError as err:
        data = Urls(error=str(err))
        logger.error("Incoming URL [{}] is broken.", url)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=data.dict()
        )

    try:
        data.urls = get_links(data.target_url)
        data = sort_urls(data)
    except (
        ConnectionError,
        TimeoutException,
        WebDriverException,
    ) as e:
        data.error = e.msg
        logger.error("Failed to parse page from url [{}].", data.target_url)
        return JSONResponse(
            status_code=status.HTTP_408_REQUEST_TIMEOUT, content=data.dict()
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content=data.dict())
