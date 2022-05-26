import requests, random

from app.logging import logger


class GitHubProxies:
    def __init__(self):
        pass

    def proxy(self):
        proxies = []
        try:
            target_url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"
            response = requests.get(target_url)
        except:
            logger.error("GitHub Proxies is either down or there is no Internet")
            quit()
        data = response.text.split("\n")[6:-3]

        for line in data:
            try:
                proxy, country, active = line.rstrip().split(" ", 2)
            except:
                continue
            if active == "+":
                proxies.append([proxy, country[:2]])

        return proxies
