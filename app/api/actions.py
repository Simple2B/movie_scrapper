import os
import time
from ..config import settings
from ..logging import logger
from .utils.parser import get_link
from .utils.scrapper import get_pages


def write_link(url):
    start_time = time.time()
    logger.info(f">>> Parser start time: {start_time}")

    if len(url.split("/")[2].split(".")) >= 3:
        website_name = url.split("/")[2].split(".")[1]
    else:
        website_name = url.split("/")[2].split(".")[0]
    logger.info(f"{website_name} site detection")
    scrapper_response = get_pages(url)

    with open(
        os.path.join(settings.FILES_PATH, "potential_cyberlockers.txt"), "w+"
    ) as pc:
        with open(
            os.path.join(settings.FILES_PATH, "potential_cyberlockers_full_urls.txt"),
            "w+",
        ) as pcfu:
            if not scrapper_response:
                err = f"TIMEOUT ocurred when scrapping {url}\n"
                pc.write(err)
                pcfu.write(err)
                logger.warning(err)
            else:
                potential_links = get_link(
                    os.path.join(settings.FILES_PATH, "movies.html"), website_name
                )
                logger.info(f"{potential_links[0]} \n {len(potential_links[0])}")
                logger.info(f"{potential_links[1]} \n {len(potential_links[1])}")
                if len(potential_links[0]) == 0:
                    pc.write(f"NOTHING FOUND => {url}\n")
                elif (
                    len(potential_links[0]) == 1
                    and "cloudflare" in potential_links[0][0]
                ):
                    pc.write(f"CLOUDFLARE BLOCK => {url}\n")
                else:
                    for link in potential_links[0]:
                        pc.write(str(link) + "\n")

                    if len(potential_links[1]) == 0:
                        pcfu.write(f"NOTHING FOUND => {url}\n")
                    elif (
                        len(potential_links[1]) == 1
                        and "cloudflare" in potential_links[1][0]
                    ):
                        pcfu.write(f"CLOUDFLARE BLOCK => {url}\n")
                    else:
                        for link in potential_links[1]:
                            pcfu.write(str(link) + "\n")
    logger.info(f">>> Scrapping and writing finished in: {time.time() - start_time}")
    return potential_links[1]
