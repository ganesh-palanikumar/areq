import requests
import areq
import asyncio


async def main():
    response = await areq.get("https://httpbin.org/get")
    print(response.text)

    response = requests.get("https://httpbin.org/get")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
