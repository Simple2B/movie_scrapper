import pytest
from typing import Generator
from fastapi.testclient import TestClient

from app.setup import create_app
from app.api.utils import encode_link


@pytest.fixture()
def client() -> Generator:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_input_movies_url(client: TestClient):

    TEST_URL = "https://123movie.so/watch-movies/american-siege.html"
    encoded_url = encode_link(TEST_URL)
    response = client.post(f"/scrap/generalist/{encoded_url}")
    assert response
