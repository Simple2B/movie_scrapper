import os
import sys

from fastapi.testclient import TestClient

from api.schemas import Urls
from client_utils import (
    encode_url,
    get_json_response,
    get_urls_to_be_scrapped_from_file,
    make_output_filepath_default_if_not_provided,
    print_data,
    print_unique_cyberlockers,
    url_need_to_be_scrapped,
    find_cyberlockers,
    find_unique_cyberlockers,
    find_unique_cyberlockers_from_a_file,
    write_data_to_csv_file,
    write_unique_cyberlockers_to_csv_file,
)
from main import app

client = TestClient(app)


def scrap(url: str) -> Urls:
    encoded_url: str = encode_url(url.strip())
    response = get_json_response(client, encoded_url)
    data: Urls = Urls(target_url=url, urls=response["urls"])
    data.cyberlockers = find_cyberlockers(data.urls)

    return data


def scrap_url():
    url_to_be_scrapped: str = os.environ.get("url", None)
    data: Urls = scrap(url_to_be_scrapped)
    data.unique_cyberlockers = find_unique_cyberlockers(data.cyberlockers)

    print_data(data)


def scrap_file():
    input_filepath = os.environ.get("input_filepath", None)

    urls_output_filepath = os.environ.get(
        "urls_output_filepath",
        make_output_filepath_default_if_not_provided("urls", input_filepath),
    )
    cyberlockers_output_filepath = os.environ.get(
        "cyberlockers_output_filepath",
        make_output_filepath_default_if_not_provided("cyberlockers", input_filepath),
    )
    unique_cyberlockers_output_filepath = os.environ.get(
        "unique_cyberlockers_output_filepath",
        make_output_filepath_default_if_not_provided(
            "unique_cyberlockers", input_filepath
        ),
    )

    urls_to_be_scrapped = get_urls_to_be_scrapped_from_file(input_filepath)

    for url in urls_to_be_scrapped:
        if url_need_to_be_scrapped(url):
            data = scrap(url)
            print_data(data)

            write_data_to_csv_file(data, urls_output_filepath, "links")
            write_data_to_csv_file(data, cyberlockers_output_filepath, "cyberlockers")

    data.unique_cyberlockers = find_unique_cyberlockers_from_a_file(
        cyberlockers_output_filepath
    )
    print_unique_cyberlockers(data.unique_cyberlockers)
    write_unique_cyberlockers_to_csv_file(
        data.unique_cyberlockers, unique_cyberlockers_output_filepath
    )


if __name__ == "__main__":
    globals()[sys.argv[1]]()
