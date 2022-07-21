import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from app.logging import logger


class SSLProxies:
    def __init__(self, url):
        self.url = url
        self.target_url = "https://www.sslproxies.org/"
        self.proxy_list = self.__proxy()

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
            logger.error("[!] SSL Proxies is either down or there is no Internet")
            quit()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.findAll("table")[0]
        rows = table.findAll("tr")

        for row in rows[1:]:
            tds = row.findAll("td")
            proxy_ip = "{}:{}".format(tds[0].get_text(), tds[1].get_text())
            country = tds[2].get_text()
            proxies.append([proxy_ip, country])
        return proxies

    def check_proxy(self, proxy_info):
        proxy_ip = proxy_info[0]

        logger.info("[+] Looking for valid IP address: {}".format(proxy_info))

        try:
            r = requests.get(
                self.url,
                proxies={
                    "http": proxy_ip,
                    "https": proxy_ip,
                },
                timeout=10,
            )

            if r.status_code != 200:
                proxy_ip = ""

        except:
            proxy_ip = ""

        return proxy_ip

    def get_proxy(self):
        with Pool() as pool:
            proxy_results = pool.map(self.check_proxy, self.proxy_list[:25])

        for chosen_proxy in proxy_results:
            if chosen_proxy: return chosen_proxy

        logger.error("[!] Unable to create connection to {}".format(self.url))
        raise WebDriverException("Unable to create connection to target URL")


if __name__ == "__main__":
    url = 'https://putlocker.today/bull/'
    proxy = SSLProxies(url)
    proxy_ip = proxy.get_proxy()
    print(proxy_ip)
