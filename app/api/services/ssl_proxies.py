import requests, random
from bs4 import BeautifulSoup

from app.logging import logger


class SSLProxies:
    def __init__(self):
        pass

    def proxy(self):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "http://www.wikipedia.org/",
            "Connection": "keep-alive",
        }
        proxies = []
        try:
            target_url = "https://www.sslproxies.org/"
            response = requests.get(url=target_url, headers=headers)
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
