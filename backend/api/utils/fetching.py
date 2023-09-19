import asyncio
import random
from typing import Any

import aiohttp
import lxml.html

from api.settings import settings

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ),
    "Referer": settings.base_url,
    "Sec-Ch-Ua-Platform": '"Linux"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
}

TOKEN = ""
RETRIED = set()


def extract_token(html_body: str) -> None:
    global TOKEN
    parser = lxml.html.fromstring(html_body)
    parsed = parser.xpath('//script[contains(@src, "Manifest.js")]/@src')
    extracted_url = next(iter(parsed), "/")
    TOKEN = extracted_url.split("/")[-2]


async def make_request(
    url: str, wait_before_request: int = 0
) -> tuple[int, dict[str, Any]]:
    global RETRIED
    if wait_before_request:
        print(f"waiting for {wait_before_request} seconds before next request...")
        await asyncio.sleep(wait_before_request)
    formatted_url = url.format(api_key=TOKEN)
    print(f"Sending request to {formatted_url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(formatted_url, headers=HEADERS) as resp:
            if resp.status == 404 and url not in RETRIED:
                print("404 status code - retrying...")
                body = await resp.text()
                extract_token(body)
                delay = random.randint(20, 40)
                print(f"waiting for {delay} seconds...")
                RETRIED.add(url)
                await asyncio.sleep(delay)
                return await make_request(url)
            elif resp.status != 200:
                return resp.status, {}
            if url in RETRIED:
                RETRIED.remove(url)
            body = await resp.json()
            return 200, body  # type: ignore
