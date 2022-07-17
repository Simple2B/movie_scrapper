import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import ElementNotInteractableException, NoSuchFrameException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
# import seleniumwire.undetected_chromedriver as uc
import undetected_chromedriver as uc

from app.api.utils import __get_configs
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
    # PROXY, country = proxy.proxyaxe, 'UK'
    logger.info("[+] Proxy of choice: " + str(PROXY))

    # Set WebDriver Options
    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-using")
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    # options.add_argument("--start-maximized")
    options.add_argument('--window-size=1920x1080')
    options.add_argument("--disable-infobars")
    options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9230")
    options.add_argument("--user-agent={}".format(user_agent))

    # Set DesiredCapabilities
    capabilities = DesiredCapabilities.CHROME.copy()

    # capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    capabilities["proxy"] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "noProxy": None,
        "proxyType": "MANUAL",
        "class": "org.openqa.selenium.Proxy",
        "autodetect": False,
    }

    # seleniumwire_options = {
    #     'proxy': {
    #         'https': PROXY,
    #     }
    # }

    driver = uc.Chrome(
        service=Service(ChromeDriverManager(path=settings.DRIVERS_DIR).install()),
        options=options,
        desired_capabilities=capabilities,
        # seleniumwire_options=seleniumwire_options
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
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    driver.save_screenshot('./screenshots/screenshot-{}.png'.format(str(random())))
    driver.set_window_size(original_size['width'], original_size['height'])


def wait_for_xpath(driver, xpath):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
    xpath_selection = driver.find_element(By.XPATH, xpath)
    return xpath_selection


def click_anchors(driver):
    """Click all anchors to load iframes if not present"""
    loader_strings = ["thumb", "mvi-cover", "splash-image", "play", "player", "playerer"]
    anchors = driver.find_elements(by=By.TAG_NAME, value="a")
    for index, anchor in enumerate(anchors):
        try:
            # Only click anchors with no redirect
            if (not anchor.get_attribute("href") and
                    any(loader in anchor.get_attribute("class") for loader in loader_strings)) or \
                    "background-image" in anchor.get_attribute("style"):
                driver.execute_script("arguments[0].click();", anchor)
        except ElementNotInteractableException:
            pass


def click_iframes(driver):
    """Click all iframes to load servers / iframe sources"""
    iframes = driver.find_elements(by=By.TAG_NAME, value="iframe")
    for index, iframe in enumerate(iframes):
        try:
            iframe.click()
        except ElementNotInteractableException:
            pass


def close_popups(driver, primary_handle):
    for handle in driver.window_handles:
        if handle != primary_handle:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(primary_handle)


def get_urls(driver):
    source = driver.page_source
    links = re.findall('"((http|ftp)s?://.*?)"', source)
    return [link[0] for link in links]


def get_cyberlockers(driver, cyberlocker_sources, links):
    # Iterate all elements but only if they have no children
    for element in driver.find_elements(By.XPATH, ".//*"):
        child_elements = element.find_elements(By.XPATH, ".//*")

        if len(child_elements) > 0: continue

        element_text = driver.execute_script("return arguments[0].textContent;", element)\
            .replace(" ", "")\
            .replace("\n", "")\
            .lower()

        if any(server in element_text.lower() for server in cyberlocker_sources):
            logger.info("[+] Selecting server: " + element_text)

            try:
                driver.execute_script("arguments[0].click();", element)
                random_timeout(10)

                # iframes = driver.find_elements(by=By.TAG_NAME, value="iframe")
                # for iframe in iframes:
                #     links.append(iframe.get_attribute('src'))
                links += get_urls(driver)

            except ElementNotInteractableException:
                logger.error("[!] Server invalid: " + element_text)

            except Exception as ex:
                logger.error("[!] Error when searching for servers: " + ex)

    for index, iframe in enumerate(driver.find_elements(By.XPATH, "//iframe")):
        try:
            links.append(iframe.get_attribute('src'))
            driver.switch_to.frame(index)
            links = get_cyberlockers(driver, cyberlocker_sources, links)

        except Exception as ex:
            logger.error("[!] Error finding server iframes")

        finally:
            driver.switch_to.parent_frame()

    return links


def get_links(url: str) -> str:
    """Return raw html page"""
    cyberlocker_sources = __get_configs().get("cyberlocker_sources")
    driver = init_driver(url)
    primary_handle = driver.current_window_handle
    links = []

    try:
        logger.info("[+] Opening url... {}".format(url))
        driver.get(url)
        random_timeout(10)

        # Debugging save screenshot
        save_screenshot(driver)

        # Iterate each anchor
        logger.info("[+] Finding movie thumbnails")
        click_anchors(driver)
        random_timeout(10)

        # Iterate each iframe
        logger.info("[+] Finding Iframes")
        click_iframes(driver)
        random_timeout(10)

        # logger.info("[+] Closing all popups")
        # close_popups(driver, primary_handle)

        logger.info("[+] Finding servers")
        links = get_cyberlockers(driver, cyberlocker_sources, links)

        return list(set(links))

    finally:
        # Get session
        logger.info("[+] Session ID: " + driver.session_id)
        logger.info("[+] Deleting all cookies...")
        driver.delete_all_cookies()
        driver.quit()
