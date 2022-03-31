import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient

from app.setup import create_app
from app.api.utils import decode_link, encode_link


@pytest.fixture()
def client() -> Generator:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_input_movies_url(client: TestClient):

    TEST_URL = "https://123movies.business/film/the-ice-road-S8TeM/"
    encoded_url = encode_link(TEST_URL)
    response = client.post(f"/scrap/generalist/{encoded_url}")
    assert response
