from typing import Annotated, Optional, Union

import strawberry
from pydantic import BaseModel, HttpUrl, field_validator
from strawberry import LazyType

from api.settings import settings
from api.types.general import Error, InputValidationError


class PydanticScanSchedule(BaseModel):
    day_of_week: int
    hour: int
    minute: int


@strawberry.experimental.pydantic.input(model=PydanticScanSchedule)
class ScanSchedule:
    day_of_week: strawberry.auto
    hour: strawberry.auto
    minute: strawberry.auto


class PydanticAdhocScanInput(BaseModel):
    url: HttpUrl
    schedule: Optional[PydanticScanSchedule] = None

    @field_validator("url")
    @classmethod
    @classmethod
    def check_url(cls, value: str) -> str:
        assert settings.base_url in str(value), "url has to contain base url"
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


AdhocScanResponse = Annotated[
    Union[InputValidationError, ScanFailedError, ScanSucceeded],
    strawberry.union("AdhocScanResponse"),
]
