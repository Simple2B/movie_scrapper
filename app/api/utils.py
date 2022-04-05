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


def url_belong_to_domain(host: str, ignored_domain: str) -> bool:
    if not ignored_domain or not host or ignored_domain not in host:
        return False
    len_sub_domain = len(host) - len(ignored_domain)
    return host[len_sub_domain:] == ignored_domain


def urls_cleanup(data: Urls) -> Urls:
    logger.info("Cleanup detected urls from [{}].", data.target_ulr)
    ignored_domains = settings.IGNORED_DOMAINS + [
        ".".join(
            data.target_ulr.host.split(".")[
                -(len(data.target_ulr.tld.split(".")) + 1) :
            ]
        )
    ]
    urls: list[str] = []
    cleaned_urls: list[str] = []
    count_deleted: int = 0
    for url in data.urls:
        for domain in ignored_domains:
            if url_belong_to_domain(
                host=url.host,
                ignored_domain=domain,
            ):
                count_deleted += 1
                break
        else:
            urls += [url]
    for url in urls:
        for extension in settings.IGNORED_EXTENSIONS:
            if url.endswith(extension):
                count_deleted += 1
                break
        else:
            cleaned_urls += [url]

    logger.info("[{}] url(s) deleted.", count_deleted)
    return Urls(target_ulr=data.target_ulr, urls=cleaned_urls)


def convert_to_xls(file_name: str, content: Urls):
    xls_data = pd.DataFrame(content.dict())
    urls_count = xls_data.urls.count()
    if os.path.exists(file_name):
        logger.info("Excel file [{}] already exists.", file_name)
        file_xls_data = pd.DataFrame(pd.read_excel(file_name))
        xls_data = pd.concat([file_xls_data, xls_data])
    xls_data.to_excel(
        file_name,
        engine="openpyxl",
        index=False,
    )
    logger.info(
        "{0} urls was detected and writted to file [{1}]", urls_count, file_name
    )
