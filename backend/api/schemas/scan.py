import random
from typing import Any

import jmespath
import strawberry
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from api.parsing import CategoryNotFoundError, parse_scan_data, parse_search_info
from api.permissions import IsAuthenticated
from api.types.general import InputValidationError
from api.types.scan import (
    AdhocScanInput,
    AdhocScanResponse,
    ScanFailedError,
    ScanSucceeded,
)
from api.utils.fetching import make_request
from api.utils.url_parsing import parse_url

TOTAL_PAGES_PATH = "pageProps.data.searchAds.pagination.totalPages"


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])  # type: ignore
    async def adhoc_scan(
        self, info: Info[Any, Any], input: AdhocScanInput
    ) -> AdhocScanResponse:
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        url = parse_url(str(data.url))
        status_code, body = await make_request(url)
        if status_code != 200:
            logger.critical(f"Scan has failed with {status_code} status code.")
            return ScanFailedError(
                message=f"Scan has failed with {status_code} status code."
            )
        session: AsyncSession = info.context["session"]
        try:
            search_event = await parse_search_info(
                str(data.url), data.schedule, body, session
            )
            await parse_scan_data(str(data.url), body, session, search_event)
        except CategoryNotFoundError:
            logger.critical(f"Parsing document for {url} has failed.")
            return ScanFailedError(message="Document parsing failed.")
        # Check for pagination
        total_pages = jmespath.search(TOTAL_PAGES_PATH, body) or 1
        if total_pages <= 1:
            return ScanSucceeded  # type: ignore
        for page_number in range(2, total_pages + 1):
            next_url = url + f"&page={page_number}"
            status_code, body = await make_request(
                url=next_url, wait_before_request=random.randint(10, 20)
            )
            await parse_scan_data(str(data.url), body, session, search_event)
        return ScanSucceeded  # type: ignore
