import pytest
from httpx import Response as HttpxResponse, Request as HttpxRequest
from requests import Response as RequestsResponse, Request as RequestsRequest
from areq.core.httpx2requests import httpx_to_requests, httpx_to_requests_response

def test_httpx_to_requests_response():
    # Create a sample httpx response
    httpx_response = HttpxResponse(
        status_code=200,
        headers={"Content-Type": "application/json", "X-Test": "test-value"},
        url="https://example.com/test",
        content=b'{"message": "Hello, World!"}',
        text='{"message": "Hello, World!"}'
    )
    
    # Convert to requests response
    requests_response = httpx_to_requests_response(httpx_response)
    
    # Verify the conversion
    assert isinstance(requests_response, RequestsResponse)
    assert requests_response.status_code == 200
    assert requests_response.headers["Content-Type"] == "application/json"
    assert requests_response.headers["X-Test"] == "test-value"
    assert requests_response.url == "https://example.com/test"
    assert requests_response.text == '{"message": "Hello, World!"}'
    assert requests_response.content == b'{"message": "Hello, World!"}'

def test_httpx_to_requests_response_with_empty_content():
    # Test with empty content
    httpx_response = HttpxResponse(
        status_code=204,
        headers={},
        url="https://example.com/empty",
        content=b'',
        text=''
    )
    
    requests_response = httpx_to_requests_response(httpx_response)
    
    assert isinstance(requests_response, RequestsResponse)
    assert requests_response.status_code == 204
    assert requests_response.headers == {}
    assert requests_response.url == "https://example.com/empty"
    assert requests_response.text == ''
    assert requests_response.content == b''

def test_httpx_to_requests_not_implemented():
    # Test that the request conversion function raises NotImplementedError
    httpx_request = HttpxRequest("GET", "https://example.com")
    with pytest.raises(NotImplementedError):
        httpx_to_requests(httpx_request)
