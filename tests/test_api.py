import os

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from app.setup import create_app
from app.api.utils import encode_link
from app.api.schemas import Urls
from app.logging import logger


@pytest.fixture()
def client() -> Generator:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_input_movies_url(client: TestClient, monkeypatch):

    TEST_URL = "https://123movie.so/watch-movies/american-siege.html"
    TEST_URLS = [
        "https://123movie.so/",
        "https://123movie.so/",
        "https://123movie.so/watch-movies/american-siege.html#",
        "https://123movie.so/cinema-movies.html",
        "https://123movie.so/recently-added.html",
        "https://123movie.so/year/2020.html",
        "https://123movie.so/genres.html",
        "https://123movie.so/genre/action.html",
        "https://123movie.so/genre/action-adventure.html",
        "https://123movie.so/genre/adult.html",
        "https://123movie.so/genre/adventure.html",
        "https://123movie.so/genre/animation.html",
        "https://123movie.so/genre/biography.html",
        "https://123movie.so/genre/browse-movies-by-genre.html",
        "https://hacker.storage.site/path/to/movie1.avi",
        "https://hacker.storage.site/path/to/movie2.avi",
        "https://hacker.storage.site/path/to/movie3.avi",
    ]

    def get_test_urls(*argv, **args):
        return TEST_URLS

    import app.api.scrapper as scrap

    monkeypatch.setattr(scrap, "get_links", get_test_urls)

    encoded_url = encode_link(TEST_URL)

    response = client.post(f"/scrap/generalist/{encoded_url}")
    assert response


def write_test_result(result: Urls):
    import pandas as pd
    from app.config import settings

    res_data = dict(
        target_url=str(result.target_ulr), num_urls=len(result.urls), error=result.error
    )
    xls_data = pd.DataFrame([res_data])
    file_name = os.path.join(
        os.path.join(settings.BASE_DIR, settings.STORAGE_FOLDER),
        "test_results.xlsx",
    )
    if os.path.exists(file_name):
        logger.info("Excel file [{}] already exists", file_name)
        file_xls_data = pd.DataFrame(pd.read_excel(file_name))
        xls_data = pd.concat([file_xls_data, xls_data])
    xls_data.to_excel(
        file_name,
        engine="openpyxl",
        index=False,
    )


load_dotenv()


@pytest.mark.skipif(
    not os.environ.get("SCRAP_TEST", None), reason="SCRAP_TEST disabled"
)
def test_all_urls(client: TestClient):

    ALL_LINKS_FILE = "target_links.txt"
    with open(ALL_LINKS_FILE, "r") as f:
        for line in f:
            if not line:
                continue
            line = line.strip()
            if line.startswith("#"):
                continue
            encoded_url = encode_link(line)
            response = client.post(f"/scrap/generalist/{encoded_url}")
            assert response
            result = Urls.parse_obj(response.json())
            write_test_result(result)
