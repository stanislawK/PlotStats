import asyncio
import random
from typing import Any

import aiohttp
import lxml.html
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_cache
from api.models.scan_failure import ScanFailure
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

cache = get_cache()


def extract_token(html_body: str) -> None:
    parser = lxml.html.fromstring(html_body)
    parsed = parser.xpath('//script[contains(@src, "Manifest.js")]/@src')
    extracted_url = next(iter(parsed), "/")
    token = extracted_url.split("/")[-2]
    cache.set("token", token)


async def make_request(
    url: str, wait_before_request: int = 0
) -> tuple[int, dict[str, Any]]:
    if wait_before_request:
        logger.info(f"waiting for {wait_before_request} seconds before next request...")
        await asyncio.sleep(wait_before_request)
    token = cache.get("token") or ""
    formatted_url = url.format(api_key=token)
    logger.info(f"Sending request to {formatted_url}")
    retries = cache.get(f"retried_{url}") or 0
    if not isinstance(retries, int):
        retries = int(retries)  # type: ignore
    async with aiohttp.ClientSession() as session:
        async with session.get(
            formatted_url, headers=HEADERS, proxy=settings.dc1_url
        ) as resp:
            if resp.status in (404, 403) and retries < 3:
                if resp.status == 403 and token != "":
                    cache.set("token", "")
                logger.warning(
                    f"{resp.status} status code - retrying {retries + 1} time..."
                )
                body = await resp.text()
                extract_token(body)
                delay = random.randint(20, 40)
                logger.info(f"waiting for {delay} seconds...")
                cache.incr(f"retried_{url}", 1)
                await asyncio.sleep(delay)
                return await make_request(url)
            if cache.get(f"retried_{url}"):
                cache.delete(f"retried_{url}")
            if resp.status != 200:
                return resp.status, {}
            body = await resp.json()
            return 200, body  # type: ignore


async def report_failure(
    status_code: int, search_id: int, session: AsyncSession
) -> None:
    failure = ScanFailure(status_code=status_code, search_id=search_id)
    session.add(failure)
    await session.commit()
