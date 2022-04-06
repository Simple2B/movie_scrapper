import os
import pytest
import json
from typing import Generator
from fastapi.testclient import TestClient
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

    BROKEN_ENCODED_STR = "abcdef123456"
    TEST_URL = "https://www.google.com/"
    TEST_BROKEN_URL = "httwww.google"

    TEST_URLS = [
        "https://www.google.com/",
        "https://mail.google.com/mail",
        "https://api.google.com/",
        "https://api.google.com/",
        "bad_urls_architecture",
        "https://github.com/",
        "https://gitlab.com/",
    ]

    def get_test_urls(*argv, **args):
        return TEST_URLS

    response = client.post(f"/api/generalist/{BROKEN_ENCODED_STR}")
    assert response.status_code == 400

    encoded_url = encode_link(TEST_BROKEN_URL)
    response = client.post(f"/api/generalist/{encoded_url}")
    assert response.status_code == 400

    import app.api.scrapper as SC

    monkeypatch.setattr(SC, "parse_page_to_links", get_test_urls)

    encoded_url = encode_link(TEST_URL)
    response = client.post(f"/api/generalist/{encoded_url}")
    assert response
    assert len(json.loads(response.content)["urls"]) == 2


def write_test_result(file_name: str, content: Urls):
    import pandas as pd

    xls_data = pd.DataFrame(
        [
            dict(
                target_url=str(content.target_url),
                num_urls=len(content.urls),
                error=content.error,
            )
        ]
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


@pytest.mark.skipif(
    not os.environ.get("SCRAP_TEST", None), reason="SCRAP_TEST disabled"
)
def test_all_urls(client: TestClient):
    from app.config import settings

    ALL_LINKS_FILE = "target_links.txt"
    TEST_RESULT_FILE: str = os.path.join(
        os.path.join(settings.BASE_DIR, settings.STORAGE_FOLDER), "test_results.xlsx"
    )
    with open(ALL_LINKS_FILE, "r") as file:
        for line in file:
            if not line or line.startswith("#"):
                continue
            encoded_url = encode_link(line.strip())
            response = client.post(f"/api/generalist/{encoded_url}")
            assert response
            data = Urls.parse_obj(response.json())
            write_test_result(file_name=TEST_RESULT_FILE, content=data)
