from typing import Optional

from httpx import (
    Headers as HttpxHeaders,
)
from httpx import (
    Request as HttpxRequest,
)
from httpx import (
    Response as HttpxResponse,
)
from requests import Request as RequestsRequest
from requests import Response as RequestsResponse
from requests.structures import CaseInsensitiveDict
from urllib3 import HTTPHeaderDict, HTTPResponse


class AreqResponse(RequestsResponse):
    def __new__(cls, httpx_response: HttpxResponse):
        return super().__new__(cls)

    def __init__(self, httpx_response: HttpxResponse):
        if httpx_response is None:
            raise ValueError("httpx_response cannot be None")

        super().__init__()
        self._httpx_response: HttpxResponse = httpx_response
        self.status_code = httpx_response.status_code
        self._content = httpx_response.content
        self.headers = CaseInsensitiveDict(httpx_response.headers)
        self.url = str(httpx_response.url)
        self.encoding = httpx_response.encoding
        self.reason = httpx_response.reason_phrase
        self.raw = HTTPResponse(
            body=httpx_response.content,
            headers=HTTPHeaderDict(httpx_response.headers),
            status=httpx_response.status_code,
            reason=httpx_response.reason_phrase,
            preload_content=False,
        )

    @property
    def httpx_response(self) -> HttpxResponse:
        return self._httpx_response


class AreqRequest(RequestsRequest):
    def __new__(cls, httpx_request: HttpxRequest):
        return super().__new__(cls)

    def __init__(self, httpx_request: HttpxRequest):
        if httpx_request is None:
            raise ValueError("httpx_request cannot be None")

        super().__init__()
        self._httpx_request: HttpxRequest = httpx_request
        self.method: str = httpx_request.method
        self.url: str = str(httpx_request.url)
        headers: HttpxHeaders = httpx_request.headers
        self.headers = CaseInsensitiveDict(headers)

    @property
    def httpx_request(self) -> HttpxRequest:
        return self._httpx_request


def create_areq_response(
    httpx_response: Optional[HttpxResponse] = None,
) -> Optional[AreqResponse]:
    """
    Factory function to create an AreqResponse from an httpx response.
    Returns None if httpx_response is None, otherwise returns an AreqResponse instance.
    """
    if httpx_response is None:
        return None
    return AreqResponse(httpx_response)


def create_areq_request(
    httpx_request: Optional[HttpxRequest] = None,
) -> Optional[AreqRequest]:
    """
    Factory function to create an AreqRequest from an httpx request.
    Returns None if httpx_request is None, otherwise returns an AreqRequest instance.
    """
    if httpx_request is None:
        return None
    return AreqRequest(httpx_request)
