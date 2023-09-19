import base64
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


def update_estate(
    existing_estate: Estate,
    new_estate: Estate,
    fields: list[str],
    session: AsyncSession,
) -> None:
    any_change = False
    for field in fields:
        new_value = getattr(new_estate, field)
        if getattr(existing_estate, field) == new_value:
            continue
        any_change = True
        setattr(existing_estate, field, new_value)
    if any_change:
        session.add(existing_estate)


async def parse_scan_data(
    url: str, body: dict[str, Any], session: AsyncSession
) -> None:
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
    encoded_url = base64.urlsafe_b64encode(url.encode("ascii"))
    search_query = select(Search).where(Search.url == encoded_url.decode("ascii"))
    search = (await session.exec(search_query)).first()  # type: ignore

    if not search:
        search = Search(
            location=jmespath.search("locations[0].fullName", search_params),
            distance_radius=search_params.get("distanceRadius"),
            coordinates=parse_coordinates(coordinates_org, coordinates_alt),
            from_price=search_params.get("priceMin"),
            to_price=search_params.get("priceMax"),
            from_surface=search_params.get("areaMin"),
            to_surface=search_params.get("areaMax"),
            category=category,
            url=encoded_url,
        )
        session.add(search)
        await session.commit()

    search_event = SearchEvent(search=search)
    session.add(search_event)
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

    # Make sure that we won't create duplicated entries for estates
    existing_estates_query = select(Estate).where(
        Estate.id.in_(estate.id for estate in estates)  # type: ignore
    )
    existing_estates = (
        await session.exec(existing_estates_query)  # type: ignore
    ).all()
    new_estates = [
        estate
        for estate in estates
        if estate.id not in (existing.id for existing in existing_estates)
    ]
    session.add_all(new_estates)
    for existing_estate in existing_estates:
        new_estate = next(
            (estate for estate in estates if estate.id == existing_estate.id)
        )
        fields_to_update = [
            "title",
            "street",
            "city",
            "province",
            "location",
            "url",
            "date_created",
        ]
        update_estate(existing_estate, new_estate, fields_to_update, session)
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
