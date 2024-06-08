import random
from typing import Any

import jmespath
import strawberry
from loguru import logger
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
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
from api.utils.fetching import handle_failed_scan, make_request
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
        base_url = str(data.url)
        url = parse_url(base_url)
        status_code, body, req_session = await make_request(url)
        session: AsyncSession = info.context["session"]
        if status_code != 200:
            await handle_failed_scan(status_code, url, base_url, session)
            return ScanFailedError(
                message=f"Scan has failed with {status_code} status code for {url}."
            )

        user = info.context["request"].state.user
        try:
            search_event = await parse_search_info(
                base_url, data.schedule, body, session, user
            )
            await parse_scan_data(base_url, body, session, search_event)
        except (CategoryNotFoundError, TypeError):
            logger.critical(f"Parsing document for {url} has failed.")
            return ScanFailedError(message="Document parsing failed.")
        # Check for pagination
        total_pages = jmespath.search(TOTAL_PAGES_PATH, body) or 1
        if total_pages <= 1:
            return ScanSucceeded  # type: ignore
        for page_number in range(2, total_pages + 1):
            next_url = url + f"&page={page_number}"
            status_code, body, req_session = await make_request(
                url=next_url,
                wait_before_request=random.randint(10, 20),
                session=req_session,
            )
            if status_code != 200:
                await handle_failed_scan(status_code, next_url, base_url, session)
                return ScanFailedError(
                    message=f"Scan has failed with {status_code} status code."
                )
            await parse_scan_data(base_url, body, session, search_event)
        return ScanSucceeded  # type: ignore
