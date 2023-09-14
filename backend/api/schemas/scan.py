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
        print(f"Sending request to {data.url}...")
        status_code, body = await make_request(data.url)
        if status_code != 200:
            return ScanFailedError(
                message=f"Scan has failed with {status_code} status code."
            )
        session: AsyncSession = info.context["session"]
        try:
            await parse_scan_data(body, session)
        except CategoryNotFoundError:
            return ScanFailedError(message="Document parsing failed.")
        return ScanSucceeded  # type: ignore
