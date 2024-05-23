import random
from typing import Any

import jmespath
from celery import current_app as celery_app
from loguru import logger
from redbeat import RedBeatSchedulerEntry

from api.database import get_async_session
from api.parsing import CategoryNotFoundError, parse_scan_data, parse_search_info
from api.schemas.scan import TOTAL_PAGES_PATH
from api.utils.celery_utils import async_task
from api.utils.fetching import handle_failed_scan, make_request
from api.utils.url_parsing import parse_url


@async_task(celery_app)  # type: ignore
async def run_periodic_scan(url: str, search_id, **kwargs: dict[str, Any]) -> None:
    logger.info(f"Running periodic scan for {url}")
    api_url = parse_url(url)
    status_code, body = await make_request(api_url)
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
                status_code, body = await make_request(
                    url=next_url, wait_before_request=random.randint(10, 20)
                )
                if status_code != 200:
                    await handle_failed_scan(
                        status_code, next_url, url, session, search_id
                    )
                try:
                    await parse_scan_data(url, body, session, search_event)
                except (CategoryNotFoundError, TypeError):
                    logger.critical(f"Parsing document for {url} has failed.")


def remove_scan_periodic_task(url: str) -> None:
    entry = None
    try:
        entry = RedBeatSchedulerEntry.from_key(f"redbeat:{url}", app=celery_app)
    except KeyError:
        pass
    if entry:
        entry.delete()
