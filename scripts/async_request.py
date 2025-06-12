import asyncio

import httpx
import requests
from httpx import Response as HttpxResponse
from requests import Response as RequestsResponse
from requests.structures import CaseInsensitiveDict

import areq


def httpx_to_requests_response(httpx_response: HttpxResponse) -> RequestsResponse:
    requests_response = RequestsResponse()
    requests_response.status_code = httpx_response.status_code
    requests_response._content = httpx_response.content
    requests_response.headers = CaseInsensitiveDict(httpx_response.headers)
    requests_response.url = str(httpx_response.url)
    requests_response.encoding = httpx_response.encoding
    requests_response.reason = httpx_response.reason_phrase

    return requests_response


async def main():
    url = "https://httpbin.org/delete"

    requests_exc = None
    areq_exc = None
    httpx_exc = None

    try:
        async with httpx.AsyncClient() as client:
            async_response = await client.get(url, follow_redirects=True)
            print(async_response.text)
    except Exception as e:
        httpx_exc = e
        print(e)

    try:
        sync_response = requests.get(url, allow_redirects=True)
        print(sync_response.text)
    except Exception as e:
        requests_exc = e
        print(e)

    try:
        areq_response = await areq.delete(url, allow_redirects=True)
        print(areq_response.text)
    except Exception as e:
        areq_exc = e
        print(e)

    print("HTTPX exception:", httpx_exc.__class__.__name__)
    print("Requests exception:", requests_exc.__class__.__name__)
    print("Areq exception:", areq_exc.__class__.__name__)


if __name__ == "__main__":
    asyncio.run(main())
