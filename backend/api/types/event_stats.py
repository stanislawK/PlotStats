from typing import Optional

import strawberry

from api.models.estate import Estate
from api.models.price import Price
from api.types.general import Error


@strawberry.type
class EventStatsInput:
    id: int
    top_prices: Optional[int]


@strawberry.experimental.pydantic.type(
    Estate,
    fields=["title", "street", "city", "province", "location", "date_created", "url"],
)
class EstateType:
    pass


@strawberry.experimental.pydantic.type(Price)
class PriceType:
    price: strawberry.auto
    price_per_square_meter: strawberry.auto
    area_in_square_meters: strawberry.auto
    terrain_area_in_square_meters: strawberry.auto
    estate: EstateType


@strawberry.type
class EventStatsType:
    avg_price: float
    avg_price_per_square_meter: float
    avg_area_in_square_meters: Optional[float]
    avg_terrain_area_in_square_meters: Optional[float]
    min_price: PriceType
    min_price_per_square_meter: PriceType
    min_prices: Optional[list[PriceType]]
    min_prices_per_square_meter: Optional[list[PriceType]]


def convert_price_from_db(price: Price) -> PriceType:
    estate_db: Estate = price.estate
    estate = EstateType(
        title=estate_db.title,
        street=estate_db.street,
        city=estate_db.city,
        province=estate_db.province,
        location=estate_db.location,
        date_created=estate_db.date_created,
        url=estate_db.url,
    )
    return PriceType(
        price=price.price,
        price_per_square_meter=price.price_per_square_meter,
        area_in_square_meters=price.area_in_square_meters,
        terrain_area_in_square_meters=price.terrain_area_in_square_meters,
        estate=estate,
    )


@strawberry.type
class SearchEventDoesntExistError(Error):
    message: str = "Search Event with provided id doesn't exist"


GetSearchEventStatsResponse = strawberry.union(
    name="GetSearchEventStatsResponse",
    types=(EventStatsType, SearchEventDoesntExistError),
)
