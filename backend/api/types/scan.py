import strawberry
from pydantic import BaseModel, HttpUrl, validator

from api.settings import settings
from api.types.general import Error, InputValidationError


class PydanticAdhocScanInput(BaseModel):
    url: HttpUrl

    @validator("url")
    @classmethod
    def check_url(cls, value: str) -> str:
        assert settings.base_url in value, "url has to contain base url"
        return value


@strawberry.experimental.pydantic.input(model=PydanticAdhocScanInput, fields=["url"])
class AdhocScanInput:
    pass


@strawberry.type
class ScanFailedError(Error):
    message: str = "Scan has failed"


@strawberry.type
class ScanSucceeded:
    message: str = "Scan has finished"


AdhocScanResponse = strawberry.union(
    "AdhocScanResponse", (InputValidationError, ScanFailedError, ScanSucceeded)
)
