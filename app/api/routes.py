from fastapi import APIRouter
from selenium.common.exceptions import TimeoutException
from app.logging import logger
from app.config import settings
from app.api.schemas import Urls

from app.api.utils import decode_link, urls_cleanup, convert_to_xls


scrapper_router = APIRouter(prefix="/scrap")


@scrapper_router.post("/generalist/{target_link_encoded}", response_model=Urls)
def input_movies_url(
    target_link_encoded: str,
) -> Urls:
    from app.api.scrapper import get_links

    url = decode_link(target_link_encoded)
    logger.info("Target URL: {}", url)
    try:
        urls = get_links(url)
        urls = urls_cleanup(urls=urls, target_url=url)
        data = Urls(target_ulr=url, urls=urls)
    except TimeoutException as e:
        data = Urls(target_ulr=url, error=e.msg)
        logger.warning("Error on target URL: {}", url)

    if settings.DEBUG and data.urls:
        convert_to_xls(data)
    return data
