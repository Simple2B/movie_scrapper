from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from base64 import binascii
from selenium.common.exceptions import TimeoutException, WebDriverException
from pydantic.error_wrappers import ValidationError
from app.logging import logger
from app.config import settings
from app.api.schemas import Urls

from app.api.utils import decode_link, urls_cleanup, convert_to_xls


scrapper_router = APIRouter(prefix="/api")


@scrapper_router.post("/generalist/{target_link_encoded}", response_model=Urls)
async def input_movies_url(
    target_link_encoded: str,
) -> Urls:
    from app.api.scrapper import parse_page_to_links, get_page

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
        data.urls = parse_page_to_links(get_page(data.target_url))
        dirty_urls_count: int = len(data.urls)
        data = urls_cleanup(data)
    except (
        TimeoutException,
        WebDriverException,
    ) as e:
        data.error = e.msg
        logger.error("Failed to parse page from url [{}].", data.target_url)
        return JSONResponse(
            status_code=status.HTTP_408_REQUEST_TIMEOUT, content=data.dict()
        )

    if not data.urls:
        data.error = "[{}] href tags found, but did not pass moderation.".format(
            dirty_urls_count
        )

    # Write all detected urls to file
    if settings.DEBUG and data.urls:
        convert_to_xls(
            file_path=settings.REQUESTS_DATA_PATH,
            content=data.dict(),
        )

    return data
