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

    TEST_URL = "https://cinema4up.org/%d9%85%d8%b4%d8%a7%d9%87%d8%af%d8%a9-%d9%81%d9%8a%d9%84%d9%85-american-siege-2021-%d9%85%d8%aa%d8%b1%d8%ac%d9%85/"
    encoded_url = encode_link(TEST_URL)
    response = client.post(f"/scrap/generalist/{encoded_url}")
    assert response
