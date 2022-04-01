from fastapi import APIRouter
from app.logging import logger
from app.config import settings
from app.api.schemas import Urls
from app.api.scrapper import get_links
from app.api.utils import decode_link, urls_cleanup, convert_to_xls


scrapper_router = APIRouter(prefix="/scrap")


@scrapper_router.post("/generalist/{target_link_encoded}", response_model=Urls)
def input_movies_url(
    target_link_encoded: str,
) -> Urls:

    url = decode_link(target_link_encoded)
    logger.info("Target URL: {}", url)
    data = urls_cleanup(Urls(target_ulr=url, urls=get_links(url)))
    convert_to_xls(data) if settings.DEBUG and data.urls else None
    return data
