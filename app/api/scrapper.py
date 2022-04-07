import re
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from app.config import settings
from app.api.utils import timer


def random_sleep(min=1, max=10):
    time.sleep(random.randrange(min, max, 1))


@timer(name="Scrapping")
def get_page(url: str) -> str:
    """Return raw html page"""
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument("--disable-extensions")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--incognito")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    # options.add_argument(f"--proxy-server={ip}")
    options.add_argument(f"user-agent={userAgent}")

    with webdriver.Chrome(
        options=options, executable_path=settings.CHROME_DRIVER_PATH
    ) as driver:
        driver.delete_all_cookies()
        driver.set_page_load_timeout(20)
        driver.get(url)
        random_sleep(6)
        return driver.execute_script("return document.documentElement.outerHTML;")


def parse_page_to_links(html: str) -> list[str]:
    """Returns list of links from html file"""
    links = re.findall('"((http|ftp)s?://.*?)"', html)
    return [link[0] for link in links]
