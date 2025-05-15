import httpx
import asyncio
import requests
from requests import Response as RequestsResponse
from requests.structures import CaseInsensitiveDict
from httpx import Response as HttpxResponse

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
    url = "https://httpbin.org/get"
    async with httpx.AsyncClient() as client:
        async_response = await client.get(url)
        print(async_response.text)

    sync_response = requests.get(url)
    print(sync_response.text)

    translated_response = httpx_to_requests_response(async_response)
    assert translated_response.text == sync_response.text, 'Responses are not equal'

if __name__ == "__main__":
    asyncio.run(main())
