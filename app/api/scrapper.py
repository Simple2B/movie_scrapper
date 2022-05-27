import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from app.logging import logger
from app.config import settings
from app.api.utils import random_timeout
from app.api.services import (
    GimmeProxies,
    UserAgents,
    Geolocation,
)


def init_driver() -> WebDriver:
    # Init User Agent
    ua: UserAgents = UserAgents()
    user_agent = ua.random_user_agent()

    # # Proxy
    # proxy = GimmeProxies()
    # PROXY, country = proxy.check_proxy()
    # logger.info("[+] Proxy of choice: " + str(PROXY))

    # Set WebDriver Options
    options = Options()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-using")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent={}".format(user_agent))

    # Set DesiredCapabilities
    # capabilities = DesiredCapabilities.CHROME.copy()

    # capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    # capabilities["proxy"] = {
    #     "httpProxy": PROXY,
    #     "ftpProxy": PROXY,
    #     "sslProxy": PROXY,
    #     "noProxy": None,
    #     "proxyType": "MANUAL",
    #     "class": "org.openqa.selenium.Proxy",
    #     "autodetect": False,
    # }
    driver = WebDriver(
        service=Service(ChromeDriverManager(path=settings.DRIVERS_DIR).install()),
        options=options,
        # desired_capabilities=capabilities,
    )

    # Confirm user agent
    agent = ua.get_user_agent(driver)
    logger.info("[+] User Agent in use: {}".format(agent))

    # Confirm GeoLocation
    # location_change = Geolocation()
    # location_change.change_geolocation(driver, country)

    return driver


def get_links(url: str) -> str:
    """Return raw html page"""
    driver = init_driver()
    try:
        logger.info("[+] Opening url...")
        driver.get(url)
        random_timeout(10)

        # a_tags = driver.find_elements(By.TAG_NAME, "a")
        # return [a.get_attribute("href") for a in a_tags]

        html = driver.execute_script("return document.documentElement.outerHTML;")
        links = re.findall('"((http|ftp)s?://.*?)"', html)
        return [link[0] for link in links]

    finally:
        # Get session
        logger.info("[+] Session ID: " + driver.session_id)
        logger.info("[+] Deleting all cookies...")
        driver.delete_all_cookies()
        driver.quit()
