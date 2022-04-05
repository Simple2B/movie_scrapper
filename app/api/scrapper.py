import os
import random
import time
from selenium import webdriver
from bs4 import BeautifulSoup as bs4
from app.logging import logger
from app.api.utils import timer


def get_driver() -> webdriver:
    """get webdriver

    Returns:
        webdriver: Chrome
    """

    logger.info("Try to use chromium driver.")

    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("log-level=3")
    return webdriver.Chrome(
        options=options, executable_path=os.path.abspath("drivers/chromedriver")
    )


@timer(name="Scrapping")
def get_links(url: str) -> list[str]:
    """scrap all links from page by the URL

    Args:
        url (str): URL for scrapping

    Returns:
        list[str]: list of all links on the page
    """

    driver: webdriver = get_driver()
    driver.set_page_load_timeout(20)
    time.sleep(random.uniform(1, 2))

    try:
        driver.get(url)
        time.sleep(random.uniform(7, 9))
        full_html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = bs4(full_html, "html.parser")
        href_tags = soup.find_all(href=True)
        # a_tags = driver.find_elements_by_xpath("//a[@href]")
        return [tag["href"] for tag in href_tags]
    finally:
        driver.quit()
