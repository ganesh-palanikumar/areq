import httpx
import pytest
import requests
from requests.structures import CaseInsensitiveDict
from urllib3 import HTTPResponse

import areq

TEST_URL = "https://httpbin.org/get"


@pytest.mark.asyncio
async def test_areq_response_creation():
    async with httpx.AsyncClient() as client:
        httpx_response = await client.get(TEST_URL)
        response = areq.AreqResponse(httpx_response)

        # Test basic properties
        assert isinstance(response, areq.AreqResponse)
        assert isinstance(response, requests.Response)
        assert response.status_code == httpx_response.status_code
        assert response.content == httpx_response.content
        assert response.url == str(httpx_response.url)
        assert response.encoding == httpx_response.encoding
        assert response.reason == httpx_response.reason_phrase

        # Test headers
        assert isinstance(response.headers, CaseInsensitiveDict)
        assert (
            response.headers["content-type"] == httpx_response.headers["content-type"]
        )

        # Test raw response
        assert isinstance(response.raw, HTTPResponse)
        assert response.raw.status == httpx_response.status_code
        assert response.raw.data == httpx_response.content

        # Test httpx_response property
        assert response.httpx_response is httpx_response


@pytest.mark.asyncio
async def test_areq_request_creation():
    async with httpx.AsyncClient() as client:
        httpx_request = client.build_request("GET", TEST_URL)
        request = areq.AreqRequest(httpx_request)

        # Test basic properties
        assert isinstance(request, areq.AreqRequest)
        assert isinstance(request, requests.Request)
        assert request.method == httpx_request.method
        assert request.url == str(httpx_request.url)

        # Test headers
        assert isinstance(request.headers, CaseInsensitiveDict)
        assert request.headers["host"] == httpx_request.headers["host"]

        # Test httpx_request property
        assert request.httpx_request is httpx_request


def test_create_areq_response_factory():
    # Test with None
    assert areq.create_areq_response(None) is None

    # Test with httpx response
    httpx_response = httpx.Response(
        status_code=200,
        content=b"test content",
        headers={"content-type": "text/plain"},
        request=httpx.Request("GET", httpx.URL("https://example.com")),
    )
    response = areq.create_areq_response(httpx_response)
    assert isinstance(response, areq.AreqResponse)
    assert response.status_code == 200
    assert response.content == b"test content"
    assert response.headers["content-type"] == "text/plain"


def test_create_areq_request_factory():
    # Test with None
    assert areq.create_areq_request(None) is None

    # Test with httpx request
    httpx_request = httpx.Request(
        "GET", "https://example.com", headers={"user-agent": "test"}
    )
    request = areq.create_areq_request(httpx_request)
    assert isinstance(request, areq.AreqRequest)
    assert request.method == "GET"
    assert request.url == "https://example.com"
    assert request.headers["user-agent"] == "test"


@pytest.mark.asyncio
async def test_response_json_parsing():
    async with httpx.AsyncClient() as client:
        httpx_response = await client.get(TEST_URL)
        response = areq.AreqResponse(httpx_response)

        # Test JSON parsing
        json_data = response.json()
        assert isinstance(json_data, dict)
        assert "url" in json_data
        assert "headers" in json_data

        # Test with invalid JSON
        httpx_response._content = b"invalid json"
        response = areq.AreqResponse(httpx_response)
        with pytest.raises(ValueError):
            response.json()


@pytest.mark.asyncio
async def test_response_text_encoding():
    async with httpx.AsyncClient() as client:
        # Test with UTF-8 content
        content = "Hello, 世界!".encode("utf-8")
        httpx_response = httpx.Response(
            status_code=200,
            content=content,
            headers={"content-type": "text/plain; charset=utf-8"},
            request=httpx.Request("GET", httpx.URL("https://example.com")),
        )
        response = areq.AreqResponse(httpx_response)
        assert response.text == "Hello, 世界!"
        assert response.encoding == "utf-8"

        # Test with different encoding
        content = "Hello, 世界!".encode("gbk")
        httpx_response = httpx.Response(
            status_code=200,
            content=content,
            headers={"content-type": "text/plain; charset=gbk"},
            request=httpx.Request("GET", httpx.URL("https://example.com")),
        )
        response = areq.AreqResponse(httpx_response)
        assert response.encoding == "gbk"
        assert response.text == "Hello, 世界!"


def test_response_raise_for_status():
    # Test with successful response
    httpx_response = httpx.Response(
        status_code=200,
        content=b"success",
        request=httpx.Request("GET", httpx.URL("https://example.com")),
    )
    response = areq.AreqResponse(httpx_response)
    response.raise_for_status()  # Should not raise

    # Test with error response
    httpx_response = httpx.Response(
        status_code=404,
        content=b"not found",
        request=httpx.Request("GET", httpx.URL("https://example.com")),
    )
    response = areq.AreqResponse(httpx_response)
    with pytest.raises(requests.exceptions.HTTPError):
        response.raise_for_status()
