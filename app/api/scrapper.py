import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import undetected_chromedriver as uc


from app.logging import logger
from app.config import settings
from app.api.utils import random_timeout
from app.api.services import (
    SSLProxies,
    UserAgents,
    Geolocation,
)
from random import random


def init_driver(url) -> WebDriver:
    # Init User Agent
    ua: UserAgents = UserAgents()
    user_agent = ua.random_user_agent()

    # # Proxy
    proxy = SSLProxies(url)
    PROXY, country = proxy.check_proxy()
    # PROXY, country = proxy.proxycrawlURL, "UK"
    logger.info("[+] Proxy of choice: " + str(PROXY))

    # Set WebDriver Options
    options = Options()

    options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-using")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9230")
    options.add_argument("--user-agent={}".format(user_agent))
    options.add_extension(".drivers/CyberlockersPlugin.zip")

    # Set DesiredCapabilities
    capabilities = DesiredCapabilities.CHROME.copy()

    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    capabilities["proxy"] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "noProxy": None,
        "proxyType": "MANUAL",
        "class": "org.openqa.selenium.Proxy",
        "autodetect": False,
    }

    driver = uc.Chrome(
        service=Service(ChromeDriverManager(path=settings.DRIVERS_DIR).install()),
        options=options,
        desired_capabilities=capabilities,
    )

    stealth(driver,
            languages=["en-GB", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    # Confirm user agent
    agent = ua.get_user_agent(driver)
    logger.info("[+] User Agent in use: {}".format(agent))

    # Confirm GeoLocation
    # location_change = Geolocation()
    # location_change.change_geolocation(driver, country)

    return driver


def save_screenshot(driver) -> None:
    # Ref: https://stackoverflow.com/a/52572919/
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    driver.find_element_by_tag_name('body').screenshot('./screenshots/screenshot-{}.png'.format(str(random())))  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])


def get_links(url: str) -> str:
    """Return raw html page"""
    driver = init_driver(url)
    try:
        logger.info("[+] Opening url... {}".format(url))
        driver.get(url)
        save_screenshot(driver)
        random_timeout(10)
        source = driver.page_source
        links = re.findall('"((http|ftp)s?://.*?)"', source)
        return [link[0] for link in links]

    finally:
        # Get session
        logger.info("[+] Session ID: " + driver.session_id)
        logger.info("[+] Deleting all cookies...")
        driver.delete_all_cookies()
        driver.quit()
