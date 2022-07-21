import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import ElementNotInteractableException, NoSuchFrameException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
# import seleniumwire.undetected_chromedriver as uc
import undetected_chromedriver as uc
import validators
from time import sleep

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
    PROXY = proxy.get_proxy()
    logger.info("[+] Proxy of choice: " + str(PROXY))

    # Set WebDriver Options
    options = Options()
    # options.add_argument("--headless")
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
                print(anchor.get_attribute('innerHTML'))

        except ElementNotInteractableException:
            pass

        except StaleElementReferenceException:
            pass


def click_iframes(driver):
    """Click all iframes to load servers / iframe sources"""
    iframes = driver.find_elements(by=By.TAG_NAME, value="iframe")
    for index, iframe in enumerate(iframes):
        try:
            driver.execute_script("arguments[0].click();", iframe)
            # iframe.click()
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
    links = re.findall('"((http|ftp)s?://.*/?)"', source)
    return [link[0] for link in links]


def get_cyberlockers(driver, cyberlocker_sources, checked, links):
    # Grab links immediately
    links += get_urls(driver)

    # Iterate all elements but only if they have no children
    potential_servers = driver.find_elements(By.TAG_NAME, "li")
    potential_servers += driver.find_elements(By.TAG_NAME, "div")
    potential_servers += driver.find_elements(By.TAG_NAME, "a")

    # for element in driver.find_elements(By.XPATH, ".//*"):
    for element in potential_servers:
        try:
            if element.get_attribute('innerHTML') in checked:
                continue
            else:
                checked.append(element.get_attribute('innerHTML'))

            child_elements = element.find_elements(By.XPATH, ".//*")

        except StaleElementReferenceException:
            child_elements = []

        if len(child_elements) > 0: continue

        try:
            element_text = driver.execute_script("return arguments[0].textContent;", element)\
                .replace(" ", "")\
                .replace("\n", "")\
                .lower()

        except StaleElementReferenceException:
            logger.error("Retrying frame")
            get_cyberlockers(driver, cyberlocker_sources, checked, links)
            return links

        # Check if parent or current element if an anchor tag
        # Open this in a new tab and click non-anchors
        parent_tag = element.find_element(By.XPATH, "..").tag_name
        new_server_url = None
        if parent_tag == 'a':
            new_server_url = element.find_element(By.XPATH, "..").get_attribute('href')
        elif element.tag_name == 'a':
            new_server_url = element.get_attribute('href')

        if len(element_text) < 20 and any(server in element_text.lower() for server in cyberlocker_sources):
            # New URL for this movie
            if validators.url(str(new_server_url)):
                logger.info("[+] Found potential new URL: " + new_server_url)
                # current_handle = driver.current_window_handle
                # driver.switch_to.new_window(WindowTypes.TAB)
                # driver.get(new_server_url)
                # driver.switch_to.window(current_handle)

            else:
                logger.info("[+] Selecting server: " + element_text)

                try:
                    driver.execute_script("arguments[0].click();", element)
                    random_timeout(10)

                except Exception as ex:
                    logger.error("[!] Error when searching for servers: " + ex)

    for index, iframe in enumerate(driver.find_elements(By.XPATH, "//iframe")):
        logger.info("Switching to new iframe")

        try:
            links.append(iframe.get_attribute('src'))
            driver.switch_to.frame(index)
            links = get_cyberlockers(driver, cyberlocker_sources, checked, links)
            driver.switch_to.parent_frame()

        except NoSuchFrameException:
            logger.error("[!] Error unknown frame")

    return links


def get_links(url: str) -> str:
    """Return raw html page"""
    cyberlocker_sources = __get_configs().get("cyberlocker_sources")
    driver = init_driver(url)
    links = []

    try:
        logger.info("[+] Opening url... {}".format(url))
        driver.get(url)
        random_timeout(10)

        # Debugging save screenshot
        # save_screenshot(driver)

        # Iterate each anchor
        logger.info("[+] Finding movie thumbnails")
        click_anchors(driver)

        # Iterate each iframe
        logger.info("[+] Finding Iframes")
        click_iframes(driver)
        random_timeout(10)

        # logger.info("[+] Closing all popups")
        # close_popups(driver, primary_handle)

        logger.info("[+] Finding servers")
        checked = []
        links = get_cyberlockers(driver, cyberlocker_sources, checked, links)

        return list(set(links))

    finally:
        # Get session
        logger.info("[+] Session ID: " + driver.session_id)
        logger.info("[+] Deleting all cookies...")
        driver.delete_all_cookies()
        driver.quit()
