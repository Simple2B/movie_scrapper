import os
import base64
from datetime import datetime
import pandas as pd
from app.logging import logger
from app.config import settings
from app.api.schemas import Urls


def decode_link(encoded_link: str) -> str:
    return base64.b64decode(encoded_link).decode("utf-8")


def encode_link(url: str) -> str:
    return base64.b64encode(url.encode()).decode("utf-8")


def timer(name: str = "Function"):
    def decrement(function):
        def wrapper(*args, **kwargs):
            start = datetime.now()
            result = function(*args, **kwargs)
            end = datetime.now()
            logger.info(
                "{name} execution time: {time.seconds}s, {time.microseconds}ms.".format(
                    time=end - start, name=name
                )
            )
            return result

        return wrapper

    return decrement


def urls_cleanup(data: Urls) -> Urls:
    result = Urls(target_ulr=data.target_ulr, error=data.error)
    ignored_domains = settings.IGNORED_DOMAINS + [data.target_ulr]
    for url in data.urls:
        for domain in ignored_domains:
            if not domain.scheme in url.scheme:
                result.urls += url
    return result


def convert_to_xls(content: Urls):
    xls_data = pd.DataFrame(content.dict())
    if os.path.exists(settings.OUTPUT_FILE):
        old_xls_data = pd.DataFrame(pd.read_excel(settings.OUTPUT_FILE))
        xls_data = pd.concat([old_xls_data, xls_data])
    xls_data.to_excel(
        settings.OUTPUT_FILE,
        engine="openpyxl",
        index=False,
    )
    logger.info("Urls was writted to file: {}", settings.OUTPUT_FILE)
