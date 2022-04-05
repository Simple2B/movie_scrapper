from fastapi import APIRouter
from base64 import binascii
from selenium.common.exceptions import TimeoutException, WebDriverException
from pydantic.error_wrappers import ValidationError
from app.logging import logger
from app.config import settings
from app.api.schemas import Urls

from app.api.utils import decode_link, urls_cleanup, convert_to_xls


scrapper_router = APIRouter(prefix="/api")


@scrapper_router.post("/generalist/{target_link_encoded}", response_model=Urls)
def input_movies_url(
    target_link_encoded: str,
) -> Urls:
    from app.api.scrapper import get_links

    try:
        url = decode_link(target_link_encoded)
        logger.info("Incoming URL detected: [{}].", url)
    except (binascii.Error, UnicodeDecodeError) as err:
        logger.error("Failed to decode incoming data [{}].", target_link_encoded)
        return Urls(error=str(err))

    try:
        Urls(target_ulr=url)
    except ValidationError as err:
        logger.error("Incoming URL [{}] is broken.", url)
        return Urls(error=str(err))

    try:
        urls: list[str] = get_links(url)
        dirty_urls_count: int = len(urls)
        data: Urls = urls_cleanup(Urls(target_ulr=url, urls=urls))
    except (
        TimeoutException,
        WebDriverException,
    ) as e:
        logger.error("Failed to parse page from url [{}].", url)
        return Urls(target_ulr=url, error=e.msg)

    if not data.urls:
        data.error = "[{}] href tags found, but did not pass moderation.".format(
            dirty_urls_count
        )

    if settings.DEBUG and data.urls:
        convert_to_xls(file_name=settings.OUTPUT_XLSX, content=data)

    return data
