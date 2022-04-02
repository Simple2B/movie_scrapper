import os
import base64
from datetime import datetime
from urllib.parse import urlparse
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


def url_belong_to_domain(url: str, domain: str) -> bool:
    if not domain:
        return False
    uri = urlparse(url)
    host = uri.hostname
    if not host or domain not in host:
        return False
    len_sub_domain = len(host) - len(domain)

    return host[len_sub_domain:] == domain


def urls_cleanup(urls: list[str], target_url: str) -> list[str]:
    target_host = urlparse(target_url).hostname
    ignored_domains = settings.IGNORED_DOMAINS + [target_host]
    result = []
    for url in urls:
        for domain in ignored_domains:
            if url_belong_to_domain(url, domain):
                break
        else:
            result += [url]
    return result


def convert_to_xls(content: Urls):
    xls_data = pd.DataFrame(content.dict())
    file_name = settings.OUTPUT_FILE
    if os.path.exists(file_name):
        logger.info("Excel file [{}] already exists", file_name)
        file_xls_data = pd.DataFrame(pd.read_excel(file_name))
        num_before = file_xls_data.urls.count()
        xls_data.update(file_xls_data)
        num_after = xls_data.urls.count()
        if num_after > num_before:
            logger.info(
                "For target {} found new {} urls",
                content.target_ulr,
                num_after - num_before,
            )
    xls_data.to_excel(
        file_name,
        engine="openpyxl",
        index=False,
    )
    logger.info("Urls was writted to file: {}", file_name)
