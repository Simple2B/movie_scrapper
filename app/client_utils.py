import base64
import csv
import json
from os.path import exists

from fastapi.testclient import TestClient

from api.schemas import Urls
from config import settings


def encode_url(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode("utf-8")


def get_json_response(client: TestClient, target_url: str):
    response = client.post(f"api/generalist/{target_url}")
    json_response = json.loads(response.content)
    return json_response


def make_output_filepath_default_if_not_provided(
    prefix: str,
    filepath: str,
) -> str:
    splitted_filepath = filepath.split("/")
    splitted_filepath[-1] = prefix + ".csv"
    result_filepath = "/".join(str(item) for item in splitted_filepath)
    return result_filepath


def get_urls_to_be_scrapped_from_file(input_filepath: str) -> list:
    with open(input_filepath, "r") as input_file:
        urls_to_be_scrapped = [line.strip() for line in input_file]
    return urls_to_be_scrapped


def url_need_to_be_scrapped(url: str) -> bool:
    if not url or url.startswith("#"):
        return False
    return True


def print_data(data: Urls) -> None:
    print("Target URL: " + data.target_url)
    print(f"All urls (Total Number: {len(data.urls)}):")

    url_number = 1
    for url in data.urls:
        print(f"{url_number}. {url}")
        url_number += 1
    print("")

    print(f"All cyberlockers (Total Number: {len(data.cyberlockers)}):")
    url_number = 1
    for cyberlocker in data.cyberlockers:
        print(f"{url_number}. {cyberlocker}")
        url_number += 1
    print("")


def print_unique_cyberlockers(unique_cyberlockers: list) -> None:
    print(f"Unique cyberlockers (Total Number: {len(unique_cyberlockers)}):")
    url_number = 1
    for cyberlocker in unique_cyberlockers:
        print(f"{url_number}. {cyberlocker}")
        url_number += 1
    print("")


def get_cyberlockers() -> list:
    with open(settings.FILTER_CONFIGS_PATH) as file:
        configs: dict = json.load(file)
    cyberlockers: list[str] = configs["cyberlockers"]
    return cyberlockers


def find_cyberlockers(urls: list) -> list:
    cyberlockers = get_cyberlockers()
    found_cyberlockers = []

    for url in urls:
        url_domain = url.host.rsplit(".", 1)[0]
        for cyberlocker in cyberlockers:
            cyberlocker_domain = cyberlocker.rsplit(".", 1)[0]
            if cyberlocker_domain == url_domain:
                found_cyberlockers.append(url)

    return found_cyberlockers


def find_unique_cyberlockers(cyberlockers: list) -> list:
    unique_cyberlockers = []
    for cyberlocker in cyberlockers:
        if cyberlocker not in unique_cyberlockers:
            unique_cyberlockers.append(cyberlocker)
    return unique_cyberlockers


def find_unique_cyberlockers_from_a_file(filepath: str) -> list:
    all_cyberlockers = []

    with open(filepath, "r") as all_cyberlockers_file:
        lines = all_cyberlockers_file.readlines()
        first_line = True
        for line in lines:
            if not first_line:
                all_cyberlockers.append(line.strip().split(",")[3])
            first_line = False

    unique_cyberlockers = find_unique_cyberlockers(all_cyberlockers)
    return unique_cyberlockers


def write_data_to_csv_file(data: Urls, filepath: str, url_type: str) -> None:

    if url_type == "links":
        if not exists(filepath):
            with open(filepath, "a+") as result_table:
                writer = csv.writer(result_table)
                writer.writerow(["Target URL", "URLs Count", "Error", "URL"])
        else:
            with open(filepath, "a+") as result_table:
                writer = csv.writer(result_table)
                first_url = True
                for url in data.urls:
                    if first_url:
                        writer.writerow(
                            [data.target_url, len(data.urls), data.error, url]
                        )
                        first_url = False
                    else:
                        writer.writerow(["", "", "", url])

    elif url_type == "cyberlockers":
        if not exists(filepath):
            with open(filepath, "a+") as result_table:
                writer = csv.writer(result_table)
                writer.writerow(["Target URL", "Cyberlockers Count", "Error", "URL"])
        else:
            with open(filepath, "a+") as result_table:
                writer = csv.writer(result_table)
                first_url = True
                for cyberlocker in data.cyberlockers:
                    if first_url:
                        writer.writerow(
                            [
                                data.target_url,
                                len(data.cyberlockers),
                                data.error,
                                cyberlocker,
                            ]
                        )
                        first_url = False
                    else:
                        writer.writerow(["", "", "", cyberlocker])


def write_unique_cyberlockers_to_csv_file(cyberlockers: list, filepath: str) -> None:
    with open(filepath, "a+") as result_table:
        writer = csv.writer(result_table)
        writer.writerow(["URL", "Count:", len(cyberlockers)])
        for cyberlocker in cyberlockers:
            writer.writerow([cyberlocker])
