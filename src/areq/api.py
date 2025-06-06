from typing import Any

from httpx import AsyncClient, HTTPError, InvalidURL
from httpx import Response as HttpxResponse

from .exceptions import convert_httpx_to_areq_exception
from .models import AreqResponse, create_areq_response


async def request(method: str, url: str, **kwargs: Any) -> AreqResponse:
    async with AsyncClient() as client:
        try:
            if "allow_redirects" in kwargs:
                kwargs["follow_redirects"] = True
                del kwargs["allow_redirects"]
            httpx_response: HttpxResponse = await client.request(method, url, **kwargs)
        except (HTTPError, InvalidURL) as e:
            raise convert_httpx_to_areq_exception(e)
        assert httpx_response is not None  # httpx client.request() never returns None
        response = create_areq_response(httpx_response)
        assert response is not None  # create_areq_response never returns None
        return response


async def get(url, params=None, **kwargs):
    return await request("get", url, params=params, **kwargs)


async def options(url, **kwargs):
    return await request("options", url, **kwargs)


async def head(url, **kwargs):
    kwargs.setdefault("allow_redirects", False)
    return await request("head", url, **kwargs)


async def post(url, data=None, json=None, **kwargs):
    return await request("post", url, data=data, json=json, **kwargs)


async def put(url, data=None, **kwargs):
    return await request("put", url, data=data, **kwargs)


async def patch(url, data=None, **kwargs):
    return await request("patch", url, data=data, **kwargs)


async def delete(url, **kwargs):
    return await request("delete", url, **kwargs)
