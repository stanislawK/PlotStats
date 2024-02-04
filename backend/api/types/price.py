import strawberry

from api.models.estate import Estate
from api.models.price import Price
from api.settings import settings
from api.types.estate import EstateType


@strawberry.experimental.pydantic.type(Price)
class PriceType:
    price: strawberry.auto
    price_per_square_meter: strawberry.auto
    area_in_square_meters: strawberry.auto
    terrain_area_in_square_meters: strawberry.auto
    estate: EstateType


def convert_price_from_db(price: Price) -> PriceType:
    estate_db: Estate = price.estate
    offer_url = f"{settings.base_url}pl/oferta/{estate_db.url}"
    estate = EstateType(
        title=estate_db.title,
        street=estate_db.street,
        city=estate_db.city,
        province=estate_db.province,
        location=estate_db.location,
        date_created=estate_db.date_created,
        url=offer_url,
    )
    return PriceType(
        price=price.price,
        price_per_square_meter=price.price_per_square_meter,
        area_in_square_meters=price.area_in_square_meters,
        terrain_area_in_square_meters=price.terrain_area_in_square_meters,
        estate=estate,
    )
