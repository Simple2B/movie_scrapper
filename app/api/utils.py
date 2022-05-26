import os
import base64
import json
import time
import random
import re
from datetime import datetime
import pandas as pd
from app.logging import logger
from app.config import settings
from app.api.schemas import Urls


def decode_link(encoded_link: str) -> str:
    return base64.urlsafe_b64decode(encoded_link).decode("utf-8")


def encode_link(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode("utf-8")


def random_timeout(min=1, max=10):
    time.sleep(random.randint(min, max))


def parse_page_to_links(html: str) -> list[str]:
    """Returns list of links from html file"""
    links = re.findall('"((http|ftp)s?://.*?)"', html)
    return [link[0] for link in links]


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


def get_ignored(data: Urls) -> dict:
    with open(settings.FILTER_CONFIGS_PATH) as file:
        configs: dict = json.load(file)
    ignored_extensions: list[str] = configs["extensions"]
    ignored_domains: list[str] = configs["domains"]
    home_domain = ".".join(
        data.target_url.host.split(".")[
            -(len(data.target_url.tld.split(".")) + 1) :  # noqa E203
        ]
    )
    domains = [
        ".".join(url.host.split(".")[-(len(url.tld.split(".")) + 1) :])  # noqa E203
        for url in data.urls
    ]
    counter = {domain: domains.count(domain) for domain in domains}
    for domain, count in counter.items():
        if count >= 10 and domain not in ignored_domains:
            ignored_domains += [domain]
    if home_domain not in ignored_domains:
        ignored_domains += [home_domain]
    return {
        "ignored_domains": ignored_domains,
        "ignored_extensions": ignored_extensions,
    }


def urls_pre_cleanup(data: Urls) -> Urls:
    data: Urls = Urls(target_url=data.target_url, urls=data.urls, error=data.error)
    cleaned_urls: list[str] = []
    for url in data.urls:
        if url.scheme and url.host and url.tld and url.path:
            cleaned_urls += [url]
    return Urls(target_url=data.target_url, urls=cleaned_urls, error=data.error)


def urls_cleanup(data: Urls) -> Urls:
    logger.info("Cleanup detected urls from [{}].", data.target_url)
    data: Urls = urls_pre_cleanup(data)
    ignored: dict = get_ignored(data)
    urls: list[str] = []
    cleaned_urls: list[str] = []
    count_deleted: int = 0
    for url in data.urls:
        for domain in ignored["ignored_domains"]:
            if url_belong_to_domain(
                host=url.host,
                ignored_domain=domain,
            ):
                count_deleted += 1
                break
        else:
            urls += [url]
    for url in urls:
        for extension in ignored["ignored_extensions"]:
            if url.endswith(extension):
                count_deleted += 1
                break
        else:
            if url.path:
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
