import httpx
import pytest
import requests
from requests.exceptions import (
    ConnectionError,
    ContentDecodingError,
    HTTPError,
    InvalidURL,
    MissingSchema,
    ProxyError,
    RequestException,
    SSLError,
    Timeout,
    TooManyRedirects,
)

import areq

TEST_URL = "https://httpbin.org"


def test_areq_exception_base():
    # Test base exception creation
    httpx_error = httpx.HTTPError("test error")
    exc = areq.AreqException(httpx_error)
    assert isinstance(exc, areq.AreqException)
    assert isinstance(exc, RequestException)
    assert exc.underlying_exception is httpx_error
    assert str(exc) == str(httpx_error)


def test_areq_http_error():
    # Test HTTP error creation
    httpx_response = httpx.Response(
        status_code=404,
        content=b"not found",
        request=httpx.Request("GET", httpx.URL("https://example.com")),
    )
    httpx_error = httpx.HTTPStatusError(
        "404 Not Found",
        request=httpx.Request("GET", httpx.URL("https://example.com")),
        response=httpx_response,
    )
    exc = areq.AreqHTTPError(httpx_error)

    assert isinstance(exc, areq.AreqHTTPError)
    assert isinstance(exc, HTTPError)
    assert isinstance(exc, areq.AreqException)
    assert exc.response is not None
    assert exc.response.status_code == 404
    assert exc.underlying_exception is httpx_error


def test_areq_connection_error():
    # Test connection error creation
    httpx_error = httpx.ConnectError("connection failed")
    exc = areq.AreqConnectionError(httpx_error)

    assert isinstance(exc, areq.AreqConnectionError)
    assert isinstance(exc, ConnectionError)
    assert isinstance(exc, areq.AreqException)
    assert exc.underlying_exception is httpx_error


def test_areq_timeout():
    # Test timeout error creation
    httpx_error = httpx.TimeoutException("request timed out")
    exc = areq.AreqTimeout(httpx_error)

    assert isinstance(exc, areq.AreqTimeout)
    assert isinstance(exc, Timeout)
    assert isinstance(exc, areq.AreqException)
    assert exc.underlying_exception is httpx_error


def test_areq_connect_timeout():
    # Test connect timeout error creation
    httpx_error = httpx.ConnectTimeout("connection timed out")
    exc = areq.AreqConnectTimeout(httpx_error)

    assert isinstance(exc, areq.AreqConnectTimeout)
    assert isinstance(exc, areq.AreqTimeout)
    assert isinstance(exc, areq.AreqConnectionError)
    assert isinstance(exc, requests.exceptions.ConnectTimeout)
    assert exc.underlying_exception is httpx_error


def test_areq_read_timeout():
    # Test read timeout error creation
    httpx_error = httpx.ReadTimeout("read timed out")
    exc = areq.AreqReadTimeout(httpx_error)

    assert isinstance(exc, areq.AreqReadTimeout)
    assert isinstance(exc, areq.AreqTimeout)
    assert isinstance(exc, requests.exceptions.ReadTimeout)
    assert exc.underlying_exception is httpx_error


def test_areq_too_many_redirects():
    # Test too many redirects error creation
    httpx_error = httpx.TooManyRedirects("too many redirects")
    exc = areq.AreqTooManyRedirects(httpx_error)

    assert isinstance(exc, areq.AreqTooManyRedirects)
    assert isinstance(exc, TooManyRedirects)
    assert isinstance(exc, areq.AreqException)
    assert exc.underlying_exception is httpx_error


def test_areq_invalid_url():
    # Test invalid URL error creation
    httpx_error = httpx.InvalidURL("invalid url")
    exc = areq.AreqInvalidURL(httpx_error)

    assert isinstance(exc, areq.AreqInvalidURL)
    assert isinstance(exc, InvalidURL)
    assert isinstance(exc, areq.AreqException)
    assert exc.underlying_exception is httpx_error


def test_areq_missing_schema():
    # Test missing schema error creation
    httpx_error = httpx.InvalidURL("missing url scheme")
    exc = areq.AreqMissingSchema(httpx_error)

    assert isinstance(exc, areq.AreqMissingSchema)
    assert isinstance(exc, MissingSchema)
    assert isinstance(exc, areq.AreqInvalidURL)
    assert exc.underlying_exception is httpx_error

    # Test that non-missing-schema errors raise ValueError
    httpx_error = httpx.InvalidURL("other invalid url error")
    with pytest.raises(ValueError):
        areq.AreqMissingSchema(httpx_error)


def test_areq_ssl_error():
    # Test SSL error creation
    httpx_error = httpx.ConnectError("ssl error")
    exc = areq.AreqSSLError(httpx_error)

    assert isinstance(exc, areq.AreqSSLError)
    assert isinstance(exc, SSLError)
    assert isinstance(exc, areq.AreqConnectionError)
    assert exc.underlying_exception is httpx_error


def test_areq_proxy_error():
    # Test proxy error creation
    httpx_error = httpx.ConnectError("proxy error")
    exc = areq.AreqProxyError(httpx_error)

    assert isinstance(exc, areq.AreqProxyError)
    assert isinstance(exc, ProxyError)
    assert isinstance(exc, areq.AreqConnectionError)
    assert exc.underlying_exception is httpx_error


def test_areq_content_decoding_error():
    # Test content decoding error creation
    httpx_error = httpx.DecodingError("decoding error")
    exc = areq.AreqContentDecodingError(httpx_error)

    assert isinstance(exc, areq.AreqContentDecodingError)
    assert isinstance(exc, ContentDecodingError)
    assert isinstance(exc, areq.AreqException)
    assert exc.underlying_exception is httpx_error


def test_convert_httpx_to_areq_exception():
    # Test conversion of various httpx errors to areq exceptions
    test_cases = [
        (
            httpx.HTTPStatusError(
                "404",
                request=httpx.Request("GET", httpx.URL("https://example.com")),
                response=httpx.Response(
                    status_code=404,
                    request=httpx.Request("GET", httpx.URL("https://example.com")),
                ),
            ),
            areq.AreqHTTPError,
        ),
        (httpx.ConnectError("connection failed"), areq.AreqConnectionError),
        (httpx.ReadTimeout("read timeout"), areq.AreqReadTimeout),
        (httpx.ConnectTimeout("connect timeout"), areq.AreqConnectTimeout),
        (httpx.WriteTimeout("write timeout"), areq.AreqTimeout),
        (httpx.PoolTimeout("pool timeout"), areq.AreqConnectTimeout),
        (httpx.TooManyRedirects("too many redirects"), areq.AreqTooManyRedirects),
        (httpx.DecodingError("decoding error"), areq.AreqContentDecodingError),
        (httpx.InvalidURL("invalid url"), areq.AreqInvalidURL),
    ]

    for httpx_error, expected_exc_type in test_cases:
        exc = areq.convert_httpx_to_areq_exception(httpx_error)
        assert isinstance(exc, expected_exc_type)
        assert exc.underlying_exception is httpx_error


def test_is_error_type():
    # Test error type checking
    httpx_error = httpx.ConnectTimeout("connect timeout")
    assert areq.is_error_type(httpx_error, httpx.ConnectTimeout)
    assert not areq.is_error_type(httpx_error, httpx.ReadTimeout)

    # Test with invalid URL
    httpx_error = httpx.InvalidURL("invalid url")
    assert areq.is_error_type(httpx_error, httpx.InvalidURL)
    assert not areq.is_error_type(httpx_error, httpx.ConnectTimeout)


@pytest.mark.asyncio
async def test_exception_with_request_and_response():
    # Test exception with both request and response
    async with httpx.AsyncClient() as client:
        try:
            await client.get(f"{TEST_URL}/status/404")
        except httpx.HTTPStatusError as httpx_error:
            exc = areq.AreqHTTPError(httpx_error)
            assert exc.request is not None
            assert exc.response is not None
            assert exc.request.method == "GET"
            assert exc.response.status_code == 404
            assert exc.underlying_exception is httpx_error
