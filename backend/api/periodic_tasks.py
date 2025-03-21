import asyncio
import random
from typing import Any

import jmespath
from celery import current_app as celery_app
from curl_cffi import requests
from loguru import logger
from redbeat import RedBeatSchedulerEntry

from api.database import get_async_session, get_cache
from api.parsing import CategoryNotFoundError, parse_scan_data, parse_search_info
from api.schemas.scan import TOTAL_PAGES_PATH
from api.settings import settings
from api.utils.celery_utils import async_task
from api.utils.fetching import handle_failed_scan, make_request
from api.utils.url_parsing import parse_url

cache = get_cache()


@async_task(celery_app)  # type: ignore
async def run_periodic_scan(url: str, search_id, **kwargs: dict[str, Any]) -> None:
    logger.info(f"Running periodic scan for {url}")
    api_url = parse_url(url)
    status_code, body, req_session = await make_request(api_url)
    async for session in get_async_session():
        if status_code != 200:
            await handle_failed_scan(status_code, api_url, url, session, search_id)
        else:
            try:
                search_event = await parse_search_info(url, None, body, session)
                await parse_scan_data(url, body, session, search_event)
            except (CategoryNotFoundError, TypeError):
                logger.critical(f"Parsing document for {url} has failed.")
        # Check for pagination
        total_pages = jmespath.search(TOTAL_PAGES_PATH, body) or 1
        if total_pages > 1:
            for page_number in range(2, total_pages + 1):
                next_url = api_url + f"&page={page_number}"
                status_code, body, req_session = await make_request(
                    url=next_url,
                    wait_before_request=random.randint(10, 20),
                    session=req_session,
                )
                if status_code != 200:
                    await handle_failed_scan(
                        status_code, next_url, url, session, search_id
                    )
                try:
                    await parse_scan_data(url, body, session, search_event)
                except (CategoryNotFoundError, TypeError):
                    logger.critical(f"Parsing document for {url} has failed.")


@async_task(celery_app)  # type: ignore
async def verify_ip(**kwargs: dict[str, Any]) -> None:
    logger.info("Verifying IP address")
    new_ip_resp = requests.get("http://ident.me/")
    new_ip: str = new_ip_resp.text
    configured_ip: str | None = cache.get("configured_ip")  # type: ignore
    if new_ip == configured_ip:
        if new_ip and len(new_ip) > 2:
            logger.info(f"No changes to IP address: ...{new_ip[-3::]}")
        else:
            logger.error(f"IP address incorrect {new_ip}")
        return
    if new_ip and len(new_ip) > 2 and configured_ip and len(configured_ip) > 2:
        logger.info(
            f"IP address changed: from ...{configured_ip[-3::]} to ...{new_ip[-3::]}"
        )
    else:
        logger.error(
            (
                f"Either new: {new_ip} or configured: {configured_ip} "
                "IP address is incorrect"
            )
        )
    zone = settings.dc1_url.split("zone-")[-1].split(":")[0]
    del_resp = requests.delete(
        settings.unblock_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.bd_token}",
        },
        json={"ip": str(configured_ip), "zone": zone},
    )
    if not del_resp.ok:
        logger.error(
            (
                f"Failed to delete IP address {configured_ip} with "
                f"status code {del_resp.status_code}"
            )
        )
    await asyncio.sleep(5)
    update_resp = requests.post(
        settings.unblock_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.bd_token}",
        },
        json={"ip": str(new_ip), "zone": zone},
    )
    if not update_resp.ok:
        logger.error(
            (
                f"Failed to unblock IP address {new_ip} with "
                f"status code {update_resp.status_code}"
            )
        )
    else:
        cache.set("configured_ip", new_ip)
        logger.info(f"New IP address set to ...{new_ip[-3::]}")


def remove_scan_periodic_task(url: str) -> None:
    entry = None
    try:
        entry = RedBeatSchedulerEntry.from_key(f"redbeat:{url}", app=celery_app)
    except KeyError:
        pass
    if entry:
        entry.delete()
