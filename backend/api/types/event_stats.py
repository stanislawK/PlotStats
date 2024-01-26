from datetime import datetime
from typing import Annotated, Optional, Union

import strawberry

from api.types.general import Error
from api.types.price import PriceType


@strawberry.input
class EventStatsInput:
    id: int
    top_prices: Optional[int] = strawberry.UNSET


@strawberry.type
class EventStatsType:
    date: Optional[datetime] = strawberry.UNSET
    avg_price: float
    avg_price_per_square_meter: float
    avg_area_in_square_meters: Optional[float] = strawberry.UNSET
    avg_terrain_area_in_square_meters: Optional[float] = strawberry.UNSET
    min_price: PriceType
    min_price_per_square_meter: PriceType
    min_prices: Optional[list[PriceType]] = strawberry.UNSET
    min_prices_per_square_meter: Optional[list[PriceType]] = strawberry.UNSET


@strawberry.type
class SearchEventDoesntExistError(Error):
    message: str = "Search Event with provided id doesn't exist"


@strawberry.type
class NoPricesFoundError(Error):
    message: str = "Search Event has no prices"


GetSearchEventStatsResponse = Annotated[
    Union[EventStatsType, SearchEventDoesntExistError, NoPricesFoundError],
    strawberry.union("GetSearchEventStatsResponse"),
]
