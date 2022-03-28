import os
import time
import base64
from app.config import settings
from app.logging import logger
from .parse_config import trash_words


def get_link(raw_html_file, website_name="fusionmovies"):
    """
    Parser function. Reads the file and gets a cyberlocker link.
    """
    potential_cyberlockers = []
    pc_full_urls = []

    start_time = time.time()
    logger.info(f">>> Parser start time: {start_time}")

    with open(raw_html_file, "r") as file:
        raw_html_data = file.read()

    for html_line in raw_html_data.split():
        try:
            if "http:" in html_line or "https:" in html_line:
                # find basic links
                http_split_line = html_line.split("/")[2]
                checker = 0
                for trash in trash_words:
                    if trash in html_line or website_name in http_split_line.split("."):
                        checker += 1
                        break
                if checker == 0 and html_line not in pc_full_urls:
                    with open(
                        os.path.join(
                            settings.FILES_PATH, "potential_cyberlockers_html_parts.txt"
                        ),
                        "a+",
                    ) as pchp:
                        pchp.write(str(html_line) + "\n")
                    pc_full_urls.append(html_line)
                    potential_cyberlockers.append(http_split_line)
            elif "ase64" in html_line:
                # find encoded links
                encoded_html = (
                    html_line.split("ase64")[-1]
                    .split(")")[0]
                    .split("decode")[-1]
                    .strip('.,"(')
                )
                try:
                    decoded_html = base64.b64decode(encoded_html)
                    if "http" in str(decoded_html):
                        for i in str(decoded_html).split():
                            if "src" in i or "href" in i:
                                decoded_link = i.split('"')[1]
                                logger.info(f"Decoded link found >>> {decoded_link}")
                                potential_cyberlockers.append(decoded_link)
                except:
                    logger.warning("Fail to decode")
        except:
            logger.warning("Fail to read html")
    logger.info(f">>> Parser finished in: {time.time() - start_time}")
    return (potential_cyberlockers, pc_full_urls)
