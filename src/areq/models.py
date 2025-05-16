from requests import Response as RequestsResponse
from requests.structures import CaseInsensitiveDict
from httpx import Response as HttpxResponse
from urllib3 import HTTPResponse, HTTPHeaderDict


class AreqResponse(RequestsResponse):
    def __init__(self, httpx_response: HttpxResponse):
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
