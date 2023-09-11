from typing import Any

import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from api.types.general import InputValidationError
from api.types.scan import AdhocScanInput, AdhocScanResponse, ScanFailedError


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
        status_code = 404
        return ScanFailedError(
            message=f"Scan has failed with {status_code} status code."
        )
