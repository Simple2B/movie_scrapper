import os, base64, json, time, random, csv
from fastapi.testclient import TestClient

from pydantic import AnyHttpUrl

from app.config import settings
from app.api.schemas import Urls


def decode_link(encoded_link: str) -> str:
    return base64.urlsafe_b64decode(encoded_link).decode("utf-8")


def encode_link(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode("utf-8")


def random_timeout(min=1, max=20):
    time.sleep(random.randint(min, max))


def __url_belong_to_domain(host: str, domain: str) -> bool:
    if not domain or not host or domain not in host:
        return False
    len_sub_domain = len(host) - len(domain)
    return host[len_sub_domain:] == domain


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
        if count >= 5 and domain not in ignored_domains:
            ignored_domains += [domain]
    if home_domain not in ignored_domains:
        ignored_domains += [home_domain]
    return {
        "extensions_end": configs.get("extensions_end"),
        "extensions_in": configs.get("extensions_in"),
        "domains": ignored_domains,
        "cyberlockers": configs.get("cyberlockers"),
        "cyberlocker_sources": configs.get("cyberlocker:sources")
    }


def sort_urls(data: Urls) -> Urls:
    from app.api.scrapper import get_links

    cleaned_urls: list[AnyHttpUrl] = __urls_cleanup(data)
    cyberlockers: list[AnyHttpUrl] = __find_cyberlockers(data)
    additional_urls: list[AnyHttpUrl] = __find_source_links(data)
    return Urls(
        target_url=data.target_url,
        urls=cleaned_urls,
        cyberlockers=cyberlockers,
        additional_urls=additional_urls,
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
        if url.path:
            urls += [url]
    return Urls(
        target_url=data.target_url,
        urls=urls,
        cyberlockers=data.cyberlockers,
        error=data.error,
    )


def __delete_ulr_by_domain(urls: list[AnyHttpUrl], domains: list) -> list[AnyHttpUrl]:
    result: list[AnyHttpUrl] = []
    for url in urls:
        for domain in domains:
            if __url_belong_to_domain(
                host=url.host,
                domain=domain,
            ):
                break
        else:
            result += [url]
    return result


def __delete_url_by_extension_end(
    urls: list[AnyHttpUrl], extensions_end: list
) -> list[AnyHttpUrl]:
    result: list[AnyHttpUrl] = []
    for url in urls:
        for extension in extensions_end:
            if url.endswith(extension):
                break
        else:
            result += [url]
    return result


def __delete_url_by_extension_in(
    urls: list[AnyHttpUrl], extensions_in: list
) -> list[AnyHttpUrl]:
    result: list[AnyHttpUrl] = []
    for url in urls:
        for extension in extensions_in:
            if extension in url:
                break
        else:
            result += [url]
    return result


def __urls_cleanup(data: Urls) -> list[AnyHttpUrl]:
    data: Urls = __urls_pre_cleanup(data)
    configs: dict = __updated_configs(data)

    stage_1: list[AnyHttpUrl] = __delete_ulr_by_domain(
        data.urls, configs.get("domains")
    )
    stage_2: list[AnyHttpUrl] = __delete_url_by_extension_end(
        stage_1, configs.get("extensions_end")
    )
    stage_3: list[AnyHttpUrl] = __delete_url_by_extension_in(
        stage_2, configs.get("extensions_in")
    )
    return stage_3


def __find_source_links(data: Urls) -> list[AnyHttpUrl]:
    data: Urls = __urls_pre_cleanup(data)
    configs: dict = __updated_configs(data)
    urls: list[AnyHttpUrl] = __delete_url_by_extension_end(
        data.urls, configs.get("extensions_end")
    )

    source_links: list[AnyHttpUrl] = []
    for url in urls:
        for cyberlocker in configs.get("cyberlockers"):
            if (
                not __url_belong_to_domain(host=url.host, domain=cyberlocker)
                and cyberlocker.split(".")[0] in url
            ):
                source_links += [url]
    return source_links


def __find_cyberlockers(data: Urls) -> list[AnyHttpUrl]:
    data: Urls = __urls_pre_cleanup(data)
    configs: dict = __updated_configs(data)

    found_cyberlockers: list[AnyHttpUrl] = []
    for url in data.urls:
        for cyberlocker in configs.get("cyberlockers"):
            if __url_belong_to_domain(
                host=url.host,
                domain=cyberlocker,
            ):
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
    splitted_filepath[-1] = prefix
    result_filepath = "/".join(str(item) for item in splitted_filepath)
    return result_filepath


def get_target_urls_from_file(input_filepath: str) -> list:
    with open(input_filepath, "r") as input_file:
        urls_to_be_scrapped = [line.strip() for line in input_file]
    return urls_to_be_scrapped


def remove_empty_lines(filename):
    if not os.path.isfile(filename):
        print("{} does not exist ".format(filename))
        return
    with open(filename) as filehandle:
        lines = filehandle.readlines()

    with open(filename, 'w') as filehandle:
        lines = filter(lambda x: x.strip(), lines)
        filehandle.writelines(lines)


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

    # Remove any empty lines introduced
    remove_empty_lines(filepath)


def write_unique_cyberlockers_to_csv_file(cyberlockers: list, filepath: str) -> None:
    with open(filepath, "a+") as result_table:
        writer = csv.writer(result_table)
        writer.writerow(["URL", "Count:", len(cyberlockers)])
        for cyberlocker in cyberlockers:
            writer.writerow([cyberlocker])


def write_source_links_to_file(data: Urls, filepath: str) -> None:
    with open(filepath, "a+") as file:
        for url in data.additional_urls:
            file.writelines(url + "\n")


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
