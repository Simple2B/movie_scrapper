import os
import re
import base64
from datetime import datetime
import pandas as pd
from tldextract import extract  # accurately separates the gTLD or ccTLD
from app.logging import logger
from app.config import settings
from app.api.schemas import Urls

IGNORED_DOMAINS: list[str] = ["whatsapp"]


def get_domain(url) -> str:
    """Get domain from url

    Args:
        url (AnyHttpUrl): valid url address

    Returns:
        str: domain_1.domain_n.com
    """
    subdomain, domain, suffix = extract(url)
    ignored = ["www", "web"]
    if not subdomain or subdomain.lower() in ignored:
        return domain
    pat = r"^(?:{})\.".format("|".join(ignored))
    return re.sub(pat, "", subdomain)


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


def urls_cleanup(domain: str, urls: list[str]) -> list[str]:
    """_summary_

    Args:
        domain (str): target url domain
        urls (list): list of all links from the page

    Returns:
        list[str]: list of cleaned links
    """

    return [url for url in urls if not domain in url]


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
