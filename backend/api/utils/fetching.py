import asyncio
import random
from typing import Any

import lxml.html
from curl_cffi import requests
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database import get_cache
from api.models.scan_failure import ScanFailure
from api.settings import settings
from api.utils.search import get_search_id_by_url

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

BROWSERS = ["chrome120", "edge101", "safari17_0"]

cache = get_cache()


def extract_token(html_body: str) -> None:
    parser = lxml.html.fromstring(html_body)
    parsed = parser.xpath('//script[contains(@src, "Manifest.js")]/@src')
    extracted_url = next(iter(parsed), "/")
    token = extracted_url.split("/")[-2]
    cache.set("token", token)


async def make_request(
    url: str,
    wait_before_request: int = 0,
    session: requests.Session | None = None,
    last_status_code: int | None = None,
) -> tuple[int, dict[str, Any], requests.Session | None]:
    await wait_before_first_request(wait_before_request)
    formatted_url = get_formatted_url(url)
    logger.info(f"Sending request to {formatted_url}")
    retries = get_number_of_retries(url)
    session = session or requests.Session(impersonate="chrome120")
    try:
        resp = session.get(formatted_url, proxies={"https": settings.dc1_url})
    except requests.errors.RequestsError:
        return 401, {}, None
    if (resp.status_code in (404, 403) and retries < 4) or (
        resp.status_code == 404 and last_status_code == 403 and retries < 7
    ):
        logger.warning(
            f"{resp.status_code} status code - retrying {retries + 1} time..."
        )
        delay = random.randint(20, 40)
        logger.info(f"waiting for {delay} seconds...")
        cache.incr(f"retried_{url}", 1)
        await asyncio.sleep(delay)
        if resp.status_code == 403:
            return await handle_403_response(url)
        body = resp.text
        extract_token(body)
        return await make_request(url, session=session, last_status_code=404)
    clean_cached_retries(url)
    if resp.status_code != 200:
        return resp.status_code, {}, None
    return handle_successful_scan(resp, session, url)


def get_formatted_url(url: str) -> str:
    token = cache.get("token") or ""
    return url.format(api_key=token)


def get_number_of_retries(url: str) -> int:
    retries = cache.get(f"retried_{url}") or 0
    if not isinstance(retries, int):
        retries = int(retries)  # type: ignore
    return retries


async def handle_403_response(
    url: str,
) -> tuple[int, dict[str, Any], requests.Session | None]:
    # For blocked requests wait longer and try other browser
    delay = random.randint(20, 40)
    new_session = requests.Session(impersonate=random.choice(BROWSERS))
    logger.info(f"waiting for {delay} seconds due to blocked request...")
    await asyncio.sleep(delay)
    cache.set("token", "")
    return await make_request(url, session=new_session, last_status_code=403)


def handle_successful_scan(
    resp: requests.Response, session: requests.Session, url: str
) -> tuple[int, dict[str, Any], requests.Session | None]:
    try:
        body = resp.json()  # type: ignore
    except ValueError:
        logger.error(f"Incorrect response body for {url}")
        return 418, {}, None
    return 200, body, session


def clean_cached_retries(url: str) -> None:
    if cache.get(f"retried_{url}"):
        cache.delete(f"retried_{url}")


async def wait_before_first_request(wait_time: int) -> None:
    if wait_time > 0:
        logger.info(f"waiting for {wait_time} seconds before next request...")
        await asyncio.sleep(wait_time)


async def report_failure(
    status_code: int, search_id: int, session: AsyncSession
) -> None:
    failure = ScanFailure(status_code=status_code, search_id=search_id)
    session.add(failure)
    await session.commit()


async def handle_failed_scan(
    status_code: int,
    scan_url: str,
    base_url: str,
    session: AsyncSession,
    search_id: int | None = None,
) -> None:
    logger.critical(f"Scan has failed with {status_code} status code for {scan_url}.")
    if not search_id:
        search_id = await get_search_id_by_url(session, str(base_url))
    if search_id:
        await report_failure(
            session=session, status_code=status_code, search_id=search_id
        )
