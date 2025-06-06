import logging

import pytest
import requests

import areq

# Test URLs
TEST_URL = "https://httpbin.org"
JSON_PLACEHOLDER = "https://jsonplaceholder.typicode.com"

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_post_json():
    url = f"{TEST_URL}/post"
    data = {"key": "value", "nested": {"array": [1, 2, 3]}}
    response = await areq.post(url, json=data)
    assert response.status_code == 200
    assert response.json()["json"] == data


@pytest.mark.asyncio
async def test_post_form_data():
    url = f"{TEST_URL}/post"
    data = {"key": "value", "file": "content"}
    response = await areq.post(url, data=data)
    assert response.status_code == 200
    assert response.json()["form"] == data


@pytest.mark.asyncio
async def test_put_json():
    url = f"{TEST_URL}/put"
    data = {"key": "updated_value"}
    response = await areq.put(url, json=data)
    assert response.status_code == 200
    assert response.json()["json"] == data


@pytest.mark.asyncio
async def test_patch_json():
    url = f"{TEST_URL}/patch"
    data = {"key": "patched_value"}
    response = await areq.patch(url, json=data)
    assert response.status_code == 200
    assert response.json()["json"] == data


# TODO: Need a better way to test this
@pytest.mark.asyncio
async def test_delete():
    url = f"{TEST_URL}/delete"
    response = await areq.delete(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_head():
    url = f"{TEST_URL}/get"
    response = await areq.head(url)
    assert response.status_code == 200
    assert response.content == b""
    assert "content-length" in response.headers


@pytest.mark.asyncio
async def test_options():
    url = f"{TEST_URL}/get"
    response = await areq.options(url)
    assert response.status_code == 200
    assert "allow" in response.headers


@pytest.mark.asyncio
async def test_request_with_headers():
    url = f"{TEST_URL}/headers"
    headers = {"X-Custom-Header": "test-value", "User-Agent": "areq-test"}
    response = await areq.get(url, headers=headers)
    assert response.status_code == 200
    assert response.json()["headers"]["X-Custom-Header"] == "test-value"
    assert response.json()["headers"]["User-Agent"] == "areq-test"


@pytest.mark.asyncio
async def test_request_with_params():
    url = f"{TEST_URL}/get"
    params = {"param1": "value1", "param2": ["value2", "value3"]}
    response = await areq.get(url, params=params)
    assert response.status_code == 200
    assert response.json()["args"]["param1"] == "value1"
    assert response.json()["args"]["param2"] == ["value2", "value3"]


@pytest.mark.asyncio
async def test_request_with_timeout():
    url = f"{TEST_URL}/delay/1"  # Endpoint that delays response by 1 second
    with pytest.raises(requests.exceptions.Timeout):
        await areq.get(url, timeout=0.1)


@pytest.mark.asyncio
async def test_request_with_cookies():
    url = f"{TEST_URL}/cookies"
    cookies = {"cookie1": "value1", "cookie2": "value2"}
    response = await areq.get(url, cookies=cookies)
    assert response.status_code == 200
    assert response.json()["cookies"] == cookies


@pytest.mark.asyncio
async def test_request_with_auth():
    url = f"{TEST_URL}/basic-auth/user/pass"
    response = await areq.get(url, auth=("user", "pass"))
    assert response.status_code == 200
    assert response.json()["authenticated"] is True


@pytest.mark.asyncio
async def test_request_with_redirects():
    url = f"{TEST_URL}/redirect/1"
    response = await areq.get(url, allow_redirects=True)
    assert response.status_code == 200
    assert response.url == f"{TEST_URL}/get"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Redirects is not working.")
async def test_request_without_redirects():
    url = f"{TEST_URL}/redirect/1"
    response = await areq.get(url, allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/get"


@pytest.mark.asyncio
async def test_request_with_invalid_json():
    url = f"{TEST_URL}/post"
    with pytest.raises(TypeError):
        await areq.post(
            url, json={"invalid": object()}
        )  # object() is not JSON serializable


@pytest.mark.asyncio
async def test_request_with_invalid_url_scheme():
    with pytest.raises(requests.exceptions.InvalidURL):
        await areq.get("invalid://url")


@pytest.mark.asyncio
async def test_request_with_invalid_method():
    response = await areq.request("INVALID", f"{TEST_URL}/get")
    assert response.status_code == 405
