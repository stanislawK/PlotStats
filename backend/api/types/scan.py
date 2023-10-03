from typing import Optional

import strawberry
from pydantic import BaseModel, HttpUrl, validator
from strawberry import LazyType

from api.settings import settings
from api.types.general import Error, InputValidationError


class PydanticScanSchedule(BaseModel):
    day_of_week: int
    hour: int
    minute: int


@strawberry.experimental.pydantic.input(
    model=PydanticScanSchedule,
    fields=[
        "day_of_week",
        "hour",
        "minute",
    ],
)
class ScanSchedule:
    pass


class PydanticAdhocScanInput(BaseModel):
    url: HttpUrl
    schedule: Optional[PydanticScanSchedule] = None

    @validator("url")
    @classmethod
    def check_url(cls, value: str) -> str:
        assert settings.base_url in value, "url has to contain base url"
        return value


@strawberry.experimental.pydantic.input(model=PydanticAdhocScanInput)
class AdhocScanInput:
    url: strawberry.auto
    schedule: Optional[LazyType["ScanSchedule", __name__]]


@strawberry.type
class ScanFailedError(Error):
    message: str = "Scan has failed"


@strawberry.type
class ScanSucceeded:
    message: str = "Scan has finished"


AdhocScanResponse = strawberry.union(
    "AdhocScanResponse", (InputValidationError, ScanFailedError, ScanSucceeded)
)
