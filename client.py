import os
import sys

from fastapi.testclient import TestClient

from app.api.schemas import Urls
from app.api.utils import (
    encode_link,
    write_data_to_csv_file,
    write_unique_cyberlockers_to_csv_file,
    get_target_urls_from_file,
    make_output_filepath,
    get_json_response,
    find_unique_cyberlockers_from_a_file,
    print_data,
    print_unique_cyberlockers,
    write_source_links_to_file,
)
from app.setup import create_app

app = create_app()
client = TestClient(app)


def scrap(url: str) -> Urls:
    encoded_url: str = encode_link(url.strip())
    response = get_json_response(client, encoded_url)
    return Urls(
        target_url=response.get("target_url"),
        urls=response.get("urls"),
        cyberlockers=response.get("cyberlockers"),
        additional_urls=response.get("additional_urls"),
        error=response.get("error"),
    )


def scrap_url():
    url: str = os.environ.get("url", None)
    data: Urls = scrap(url)
    print_data(data)


def scrap_file():
    # if no path use test file
    try:
        input_filepath = os.environ.get("input_filepath", None)
        urls_output_filepath = make_output_filepath("urls.csv", input_filepath)

    except AttributeError as e:
        # input_filepath = "./tests/88_ulrs_test_-_Bull.txt"
        input_filepath = "./tests/small_test.txt"
        urls_output_filepath = make_output_filepath("urls.csv", input_filepath)

    target_urls_output_filepath = make_output_filepath(
        "target_links.txt", input_filepath
    )
    cyberlockers_output_filepath = make_output_filepath(
        "cyberlockers.csv", input_filepath
    )
    unique_cyberlockers_output_filepath = make_output_filepath(
        "unique_cyberlockers.csv", input_filepath
    )
    urls = get_target_urls_from_file(input_filepath)

    for url in urls:
        data = scrap(url)
        print_data(data)
        write_data_to_csv_file(data, urls_output_filepath, "links")
        write_data_to_csv_file(data, cyberlockers_output_filepath, "cyberlockers")
        write_source_links_to_file(data, target_urls_output_filepath)

    unique_cyberlockers = find_unique_cyberlockers_from_a_file(
        cyberlockers_output_filepath
    )
    print_unique_cyberlockers(unique_cyberlockers)
    if unique_cyberlockers:
        write_unique_cyberlockers_to_csv_file(
            unique_cyberlockers, unique_cyberlockers_output_filepath
        )


if __name__ == "__main__":
    globals()[sys.argv[1]]()
