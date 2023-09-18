import logging
from typing import Any

import strawberry
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from api.parsing import CategoryNotFoundError, parse_scan_data
from api.types.general import InputValidationError
from api.types.scan import (
    AdhocScanInput,
    AdhocScanResponse,
    ScanFailedError,
    ScanSucceeded,
)
from api.utils.fetching import make_request
from api.utils.url_parsing import parse_url


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def adhoc_scan(
        self, info: Info[Any, Any], input: AdhocScanInput
    ) -> AdhocScanResponse:
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        url = parse_url(data.url)
        logging.info(f"Sending request to {url}...")
        status_code, body = await make_request(url)
        if status_code != 200:
            logging.error(f"Scan has failed with {status_code} status code.")
            return ScanFailedError(
                message=f"Scan has failed with {status_code} status code."
            )
        session: AsyncSession = info.context["session"]
        try:
            await parse_scan_data(data.url, body, session)
        except CategoryNotFoundError:
            return ScanFailedError(message="Document parsing failed.")
        return ScanSucceeded  # type: ignore
