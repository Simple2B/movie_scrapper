import requests, random
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from app.logging import logger


class SSLProxies:
    def __init__(self):
        self.url = "https://www.google.com/"
        self.target_url = "https://www.sslproxies.org/"

    def __proxy(self):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "http://www.wikipedia.org/",
            "Connection": "keep-alive",
        }
        # Define the IP and Port list
        proxies = []
        try:
            response = requests.get(url=self.target_url, headers=headers)
        except:
            logger.error("SSL Proxies is either down or there is no Internet")
            quit()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.findAll("table")[0]
        rows = table.findAll("tr")

        for row in rows[1:]:
            tds = row.findAll("td")
            PROXY = "{}:{}".format(tds[0].get_text(), tds[1].get_text())
            country = tds[2].get_text()
            proxies.append([PROXY, country])
        return proxies

    def check_proxy(self):
        proxy_found = False
        counter = 0
        PROXY, country = "", ""
        while not proxy_found:
            if counter == 60:
                logger.error("Unable to create connection to {}".format(self.url))
                raise WebDriverException("Unable to create connection to target URL")
            proxy_choice = random.choice(self.__proxy())
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
