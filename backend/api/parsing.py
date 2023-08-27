from typing import Any

import jmespath
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.models import Category, Estate, Price, Search, SearchEvent

CATEGORY_MAP = {"terrain": "Plot", "flat": "Apartment", "house": "House"}


class CategoryNotFoundError(Exception):
    pass


def parse_coordinates(
    coordinates_org: dict[str, str | float] | None,
    coordinates_alt: dict[str, str | float] | None,
) -> str:
    coordinates = coordinates_org or coordinates_alt
    if not coordinates:
        return ""
    coordinates.pop("__typename", None)
    output = ""
    for key, value in coordinates.items():
        output += f"{key}: {value}, "
    return output.removesuffix(", ")


async def parse_scan_data(body: dict[str, Any], session: AsyncSession) -> None:
    coordinates_org = jmespath.search("pageProps.mapBoundingBox.boundingBox", body)
    coordinates_alt = jmespath.search("pageProps.data.searchMapPins.boundingBox", body)

    estate_type = jmespath.search("pageProps.estate", body) or ""
    cat_query = select(Category).where(
        Category.name == CATEGORY_MAP[estate_type.lower()]
    )

    category = (await session.exec(cat_query)).first()  # type: ignore
    if not category:
        raise CategoryNotFoundError

    search_params = jmespath.search("pageProps.filteringQueryParams", body)

    search = Search(
        location=jmespath.search("locations[0].fullName", search_params),
        distance_radius=search_params.get("distanceRadius"),
        coordinates=parse_coordinates(coordinates_org, coordinates_alt),
        from_price=search_params.get("priceMin"),
        to_price=search_params.get("priceMax"),
        from_surface=search_params.get("areaMin"),
        to_surface=search_params.get("areaMax"),
        category=category,
    )

    search_event = SearchEvent(search=search)
    session.add_all([search, search_event])
    await session.commit()

    ads = jmespath.search("pageProps.data.searchAds.items", body)
    estates = [
        Estate(
            id=ad.get("id"),
            title=ad.get("title", ""),
            street=jmespath.search("location.address.street.name", ad),
            city=jmespath.search("location.address.city.name", ad),
            province=jmespath.search("location.address.province.name", ad),
            location=jmespath.search("locationLabel.value", ad),
            date_created=ad.get("dateCreatedFirst") or ad.get("dateCreated"),
            url=ad.get("slug"),
        )
        for ad in ads
    ]
    session.add_all(estates)
    prices = [
        Price(
            price=jmespath.search("totalPrice.value", ad),
            price_per_square_meter=jmespath.search("pricePerSquareMeter.value", ad),
            area_in_square_meters=ad.get("areaInSquareMeters"),
            terrain_area_in_square_meters=ad.get("terrainAreaInSquareMeters"),
            estate_id=ad.get("id"),
            search_event=search_event,
        )
        for ad in ads
    ]
    session.add_all(prices)
    await session.commit()
