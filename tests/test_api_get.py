import pytest
import requests
from requests.exceptions import (
    ConnectionError,
    MissingSchema,
    SSLError,
    TooManyRedirects,
)

import areq


@pytest.mark.asyncio
async def test_get_success():
    url = "https://jsonplaceholder.typicode.com/posts/1"
    response = await areq.get(url)
    assert isinstance(response, areq.AreqResponse)
    assert isinstance(response, requests.Response)
    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["id"] == 1
    assert response.json()["title"] is not None
    assert response.json()["body"] is not None

    req_response = requests.get(url)
    assert req_response.json() == response.json()
    assert req_response.status_code == response.status_code
    assert req_response.content == response.content
    assert req_response.text == response.text
    assert req_response.url == response.url
    assert req_response.encoding == response.encoding


@pytest.mark.asyncio
async def test_get_failure():
    url = "https://jsonplaceholder.typicode.com/1"
    response = await areq.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_url():
    url = "not-a-valid-url"
    with pytest.raises(MissingSchema):
        await areq.get(url)


@pytest.mark.asyncio
async def test_connection_timeout():
    url = "http://10.255.255.255"  # Non-routable IP
    timeout = 0.1  # Very short timeout to ensure it fails quickly

    with pytest.raises(ConnectionError):
        await areq.get(url, timeout=timeout)


@pytest.mark.asyncio
async def test_dns_failure():
    url = "http://this-domain-does-not-exist-123456789.com"
    with pytest.raises(ConnectionError):
        await areq.get(url)


@pytest.mark.asyncio
async def test_ssl_error():
    url = "https://expired.badssl.com"  # Known expired SSL certificate
    with pytest.raises(SSLError):
        await areq.get(url)


@pytest.mark.asyncio
@pytest.mark.skip(reason="Too many redirects is not firing an exception")
async def test_too_many_redirects():
    url = "https://httpbin.org/redirect/6"  # More than default max redirects
    with pytest.raises(TooManyRedirects):
        await areq.get(url)
