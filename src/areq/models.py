from requests import Response as RequestsResponse, Request as RequestsRequest
from requests.structures import CaseInsensitiveDict
from httpx import (
    Response as HttpxResponse,
    Request as HttpxRequest,
    Headers as HttpxHeaders,
)
from urllib3 import HTTPResponse, HTTPHeaderDict


class AreqResponse(RequestsResponse):
    def __new__(cls, httpx_response: HttpxResponse | None = None):
        if not httpx_response:
            return None
        return super().__new__(cls)

    def __init__(self, httpx_response: HttpxResponse | None = None):
        if not httpx_response:
            return

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
    def __new__(cls, httpx_request: HttpxRequest | None = None):
        if not httpx_request:
            return None
        return super().__new__(cls)

    def __init__(self, httpx_request: HttpxRequest | None = None):
        if not httpx_request:
            return

        super().__init__()
        self._httpx_request: HttpxRequest = httpx_request
        self.method: str = httpx_request.method
        self.url: str = str(httpx_request.url)
        headers: HttpxHeaders = httpx_request.headers
        self.headers = CaseInsensitiveDict(headers)

    @property
    def httpx_request(self) -> HttpxRequest:
        return self._httpx_request
