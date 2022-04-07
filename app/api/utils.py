import os
import base64
import json
from datetime import datetime
import requests
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
    data: Urls = Urls(target_url=data.target_url, urls=data.urls, error=data.error)
    logger.info("Cleanup detected urls from [{}].", data.target_url)

    with open(settings.FILTER_CONFIGS_PATH) as file:
        configs: dict = json.load(file)

    ignored_extensions: list[str] = configs["ignored_extensions"]
    ignored_domains: list[str] = configs["ignored_domains"] + [
        ".".join(
            data.target_url.host.split(".")[
                -(len(data.target_url.tld.split(".")) + 1) :  # noqa E203
            ]
        )
    ]
    urls: list[str] = []
    cleaned_urls: list[str] = []
    count_deleted: int = 0
    for url in data.urls:
        if not all([url.scheme, url.tld]):
            continue
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
        for extension in ignored_extensions:
            if url.endswith(extension):
                count_deleted += 1
                break
        else:
            cleaned_urls += [url]

    logger.info("[{}] url(s) deleted.", count_deleted)
    return Urls(target_url=data.target_url, urls=cleaned_urls, error=data.error)


def convert_to_xls(file_path: str, content: dict):
    xls_data: pd.DataFrame = pd.DataFrame(content)
    if os.path.exists(file_path):
        logger.info("Excel file [{}] already exists.", file_path)
        file_xls_data = pd.DataFrame(pd.read_excel(file_path))
        xls_data = pd.concat([file_xls_data, xls_data])
    xls_data.to_excel(
        file_path,
        engine="openpyxl",
        index=False,
    )
    logger.info("File has been written to [{}].", file_path)
