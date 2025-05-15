from typing import Any
from httpx import AsyncClient, Response as HttpxResponse
from .models import AreqResponse


async def request(method: str, url: str, **kwargs: Any) -> AreqResponse:
    async with AsyncClient() as client:
        httpx_response: HttpxResponse = await client.request(method, url, **kwargs)
        return AreqResponse(httpx_response)


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
