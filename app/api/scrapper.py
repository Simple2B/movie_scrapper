import re, random, time, requests, os, itertools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from app.logging import logger
from app.config import settings
from app.api.utils import timer, random_timeout
from app.api.services import (
    SSLProxies,
    GitHubProxies,
    GimmeProxies,
    UserAgents,
    Geolocation,
)


# Confirm proxy's validity
def check_proxy(proxy_choices, url):
    proxies = [proxy_choices["gimme_proxies"]] + list(
        itertools.chain(proxy_choices["ssl_proxies"], proxy_choices["github_proxies"])
    )
    proxy_found = False
    counter = 0
    PROXY, country = "", ""
    while not proxy_found:
        if counter == 20:
            logger.error("Unable to create connection to {}".format(url))
            raise WebDriverException("Unable to create connection to target URL")
        proxy_choice = random.choice(proxies)
        PROXY, country = proxy_choice
        counter += 1
        logger.info(
            "[+] Looking for valid IP address: {} >>> {}".format(
                str(counter), proxy_choice
            )
        )
        try:
            r = requests.get(
                url,
                proxies={
                    "http": PROXY,
                    "https": PROXY,
                },
                timeout=8,
            )
            if r.status_code == 200:
                logger.info("\n[+] IP Address used as proxy: " + PROXY)
                proxy_found = True
            else:
                PROXY, country = proxy_choice
        except:
            PROXY, country = proxy_choice
    return PROXY, country


@timer(name="Scrapping")
def get_page(url: str) -> str:
    """Return raw html page"""
    useragents = UserAgents()
    user_agent = useragents.random_user_agent()

    # Proxy
    ssl_proxies = SSLProxies()
    github_proxies = GitHubProxies()
    gimme_proxies = GimmeProxies()
    proxy_choices = {
        "ssl_proxies": ssl_proxies.proxy(),
        "github_proxies": github_proxies.proxy(),
        "gimme_proxies": gimme_proxies.proxy(),
    }

    PROXY, country = check_proxy(proxy_choices, url)
    logger.info("[+] Proxy of choice: " + str(PROXY))

    # Set Chromedriver Options
    options = Options()

    # options.add_argument('--headless')
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
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities["acceptInsecureCerts"] = True
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
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(path=settings.DRIVERS_DIR).install()),
        options=options,
        desired_capabilities=capabilities,
    )

    # Confirm user agent
    agent = useragents.get_user_agent(driver)
    logger.info("[+] User Agent in use: {}".format(agent))
    location_change = Geolocation()
    location_change.change_geolocation(driver, country)

    try:
        logger.info("[+] Opening url...")
        driver.get(url)
        random_timeout(8)
        return driver.execute_script("return document.documentElement.outerHTML;")
    finally:
        # Get session
        logger.info("[+] Session ID: " + driver.session_id)
        logger.info("[+] Deleting all cookies...")
        driver.delete_all_cookies()
        driver.quit()
