from typing import Any

import strawberry
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from api.parsing import parse_scan_data
from api.types.general import InputValidationError
from api.types.scan import AdhocScanInput, AdhocScanResponse, ScanFailedError
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
        session: AsyncSession = info.context["session"]
        await parse_scan_data(body, session)
        print(status_code)
        print(body)
        status_code = 404
        return ScanFailedError(
            message=f"Scan has failed with {status_code} status code."
        )
