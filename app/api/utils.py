import os, base64, json, time, random, csv
from fastapi.testclient import TestClient

from pydantic import AnyHttpUrl

from app.config import settings
from app.api.schemas import Urls


def decode_link(encoded_link: str) -> str:
    return base64.urlsafe_b64decode(encoded_link).decode("utf-8")


def encode_link(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode("utf-8")


def random_timeout(min=1, max=60):
    time.sleep(random.randint(min, max))


def __url_belong_to_domain(host: str, ignored_domain: str) -> bool:
    if not ignored_domain or not host or ignored_domain not in host:
        return False
    len_sub_domain = len(host) - len(ignored_domain)
    return host[len_sub_domain:] == ignored_domain


def __get_configs(path: str = settings.FILTER_CONFIGS_PATH) -> dict:
    with open(path) as file:
        configs: dict = json.load(file)
    return configs


def __updated_configs(data: Urls) -> dict:
    configs = __get_configs()
    ignored_domains = configs.get("domains")
    home_domain = ".".join(
        data.target_url.host.split(".")[
            -(len(data.target_url.tld.split(".")) + 1) :  # noqa E203
        ]
    )
    domains = [
        ".".join(url.host.split(".")[-(len(url.tld.split(".")) + 1) :])  # noqa E203
        for url in data.urls
    ]
    counter = {domain: domains.count(domain) for domain in domains}
    for domain, count in counter.items():
        if count >= 10 and domain not in ignored_domains:
            ignored_domains += [domain]
    if home_domain not in ignored_domains:
        ignored_domains += [home_domain]
    return {
        "extensions_end": configs.get("extensions_end"),
        "extensions_in": configs.get("extensions_in"),
        "domains": ignored_domains,
        "cyberlockers": configs.get("cyberlockers"),
    }


def sort_urls(data: Urls) -> Urls:
    cleaned_urls: list[AnyHttpUrl] = __urls_cleanup(data)
    cyberlockers: list[AnyHttpUrl] = __find_cyberlockers(data)
    return Urls(
        target_url=data.target_url,
        urls=cleaned_urls,
        cyberlockers=cyberlockers,
        error=data.error,
    )


def __urls_pre_cleanup(data: Urls) -> Urls:
    data: Urls = Urls(
        target_url=data.target_url,
        urls=data.urls,
        cyberlockers=data.cyberlockers,
        error=data.error,
    )
    urls: list[AnyHttpUrl] = []
    for url in data.urls:
        if url.scheme and url.host and url.tld and url.path:
            urls += [url]
    return Urls(
        target_url=data.target_url,
        urls=urls,
        cyberlockers=data.cyberlockers,
        error=data.error,
    )


def __urls_cleanup(data: Urls) -> list[AnyHttpUrl]:
    data: Urls = __urls_pre_cleanup(data)
    configs: dict = __updated_configs(data)
    stage_1_cleaned_urls: list[AnyHttpUrl] = []
    stage_2_cleaned_urls: list[AnyHttpUrl] = []
    stage_3_cleaned_urls: list[AnyHttpUrl] = []
    for url in data.urls:
        for domain in configs.get("domains"):
            if __url_belong_to_domain(
                host=url.host,
                ignored_domain=domain,
            ):
                break
        else:
            stage_1_cleaned_urls += [url]
    for url in stage_1_cleaned_urls:
        for extension in configs.get("extensions_end"):
            if url.endswith(extension):
                break
        else:
            stage_2_cleaned_urls += [url]
    for url in stage_2_cleaned_urls:
        for extension in configs.get("extensions_in"):
            if extension in url:
                break
        else:
            stage_3_cleaned_urls += [url]
    return stage_3_cleaned_urls


def __find_cyberlockers(data: Urls) -> list[AnyHttpUrl]:
    data: Urls = __urls_pre_cleanup(data)
    configs: dict = __updated_configs(data)

    found_cyberlockers: list = []
    for url in data.urls:
        for cyberlocker in configs.get("cyberlockers"):
            if cyberlocker in url:
                found_cyberlockers += [url]
    return found_cyberlockers


def get_json_response(client: TestClient, target_link_encoded: str):
    response = client.post(f"api/generalist/{target_link_encoded}")
    return json.loads(response.content)


def make_output_filepath(
    prefix: str,
    filepath: str,
) -> str:
    splitted_filepath = filepath.split("/")
    splitted_filepath[-1] = prefix + ".csv"
    result_filepath = "/".join(str(item) for item in splitted_filepath)
    return result_filepath


def get_target_urls_from_file(input_filepath: str) -> list:
    with open(input_filepath, "r") as input_file:
        urls_to_be_scrapped = [line.strip() for line in input_file]
    return urls_to_be_scrapped


def write_data_to_csv_file(data: Urls, filepath: str, url_type: str) -> None:

    if url_type == "links":
        if not os.path.exists(filepath):
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
        if not os.path.exists(filepath):
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


def write_unique_cyberlockers_to_csv_file(data: Urls, filepath: str) -> None:
    with open(filepath, "a+") as result_table:
        writer = csv.writer(result_table)
        writer.writerow(["URL", "Count:", len(data.cyberlockers)])
        for cyberlocker in data.cyberlockers:
            writer.writerow([cyberlocker])


def find_unique_cyberlockers_from_a_file(filepath: str) -> list:
    cyberlockers = []
    unique_cyberlockers = []
    with open(filepath, "r") as file:
        lines = file.readlines()
        first_line = True
        for line in lines:
            if not first_line:
                cyberlockers.append(line.strip().split(",")[3])
            first_line = False
    for cyberlocker in cyberlockers:
        if cyberlocker not in unique_cyberlockers:
            unique_cyberlockers.append(cyberlocker)
    return unique_cyberlockers


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
