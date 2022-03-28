import os
from selenium import webdriver
import random
import time
from app.config import settings
from app.logging import logger
from .parse_config import drivers


def get_driver() -> webdriver:
    """Driver selenium function"""

    driver = random.choice(list(drivers.items()))
    logger.info(f">>> Try to use {driver[0]} driver")

    if driver[0] == "chromium":
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
            options=options, executable_path=os.path.abspath(driver[1])
        )
    elif driver[0] == "firefox":
        from selenium.webdriver.firefox.options import Options

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-infobars")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        return webdriver.Firefox(
            options=options, executable_path=os.path.abspath(driver[1])
        )
    else:
        raise logger.warning(">>> Can't find any drivers")


def get_pages(url: str) -> bool:
    """
    Scrapper function. Launches Selenium webdriver, scrapes website html and writes html to file.
    """

    start_time = time.time()
    logger.info(f">>> Scrapper start time: {start_time}")
    driver: webdriver = get_driver()
    driver.set_page_load_timeout(20)
    time.sleep(random.uniform(1, 2))
    logger.info(f"--- {time.time() - start_time} seconds")

    try:
        driver.get(url)
        time.sleep(random.uniform(6, 7))
        logger.info(f"--- {time.time() - start_time} seconds")
        outer_html = driver.execute_script("return document.documentElement.outerHTML;")
    except:
        logger.warning(f"Error ocurred when scrapping: {url}")
        logger.info(f">>> Scrapper finished in: {time.time() - start_time}")
        driver.quit()
        return False

    with open(os.path.join(settings.FILES_PATH, "movies.html"), "w+") as f:
        f.write(str(outer_html))

    logger.info(f">>> Scrapper finished in: {time.time() - start_time}")
    driver.quit()
    return True
