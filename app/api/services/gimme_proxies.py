import requests, json
from selenium.common.exceptions import WebDriverException


from app.logging import logger


class GimmeProxies:
    def __init__(self):
        self.url = "https://www.google.com/"
        self.target_url = "http://gimmeproxy.com/api/getProxy?country=US"

    def __proxy(self):
        try:
            response = requests.get(self.target_url)
        except:
            logger.error("Gimme Proxies is either down or there is no Internet.")
            quit()
        proxy: dict = json.loads(response.text)
        country: str = proxy.get("country")
        PROXY: str = "{}:{}".format(proxy.get("ip"), proxy.get("port"))
        return [PROXY, country]

    def check_proxy(self):
        proxy_found = False
        counter = 0
        PROXY, country = "", ""
        while not proxy_found:
            if counter == 60:
                logger.error("Unable to create connection to {}".format(self.url))
                raise WebDriverException("Unable to create connection to target URL")
            proxy_choice = self.__proxy()
            PROXY, country = proxy_choice
            counter += 1
            logger.info(
                "[+] Looking for valid IP address: {} >>> {}".format(
                    str(counter), proxy_choice
                )
            )
            try:
                r = requests.get(
                    self.url,
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
