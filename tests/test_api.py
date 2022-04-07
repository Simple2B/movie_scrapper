import os
import pytest
import json
from typing import Generator
from fastapi.testclient import TestClient
from app.setup import create_app
from app.api.utils import encode_link, convert_to_xls


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


@pytest.mark.skipif(
    not os.environ.get("SCRAP_TEST", None), reason="SCRAP_TEST disabled"
)
def test_all_urls(client: TestClient):
    from app.config import settings

    with open(settings.TARGET_LINKS_PATH, "r") as file:
        for line in file:
            if not line or line.startswith("#"):
                continue
            encoded_url = encode_link(line.strip())
            response = client.post(f"/api/generalist/{encoded_url}")
            assert response
            json_response = json.loads(response.content)
            data = dict(
                target_url=json_response["target_url"],
                urls_count=len(json_response["urls"]),
                error=json_response["error"],
            )
            convert_to_xls(
                file_path=settings.STATISTICS_DATA_PATH,
                content=[data],
            )
