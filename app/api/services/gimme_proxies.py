import requests, json

from app.logging import logger


class GimmeProxies:
    def __init__(self):
        pass

    def proxy(self):
        try:
            target_url = "http://gimmeproxy.com/api/getProxy?country=US"
            response = requests.get(target_url)
        except:
            logger.error("Gimme Proxies is either down or there is no Internet")
            quit()
        output = json.loads(response.text)
        country = output["country"]
        PROXY = "{}:{}".format(output["ip"], output["port"])
        return [PROXY, country]
