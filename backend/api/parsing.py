from typing import Any
from api.models import Category, Search, SearchEvent, Estate, Price
from sqlmodel import select
import jmespath
from sqlalchemy.ext.asyncio import AsyncSession

"""
class Estate(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    street: Optional[str] = Field(default=None)
    city: Optional[str] = Field(index=True)
    province: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    date_created: Optional[datetime] = Field(default=None)
    url: str
    search_events: List[SearchEvent] = Relationship(
        back_populates="estates", link_model=SearchEventEstate
    )
    prices: List["Price"] = Relationship(back_populates="estate")

class Price(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    price: int
    price_per_square_meter: Optional[int] = Field(default=None)
    area_in_square_meters: Optional[int] = Field(default=None)
    terrain_area_in_square_meters: Optional[int] = Field(default=None)
    estate_id: Optional[int] = Field(default=None, foreign_key="estate.id")
    estate: Estate = Relationship(back_populates="prices")
    search_event_id: Optional[int] = Field(default=None, foreign_key="searchevent.id")
    search_event: "SearchEvent" = Relationship(back_populates="prices")

class SearchEventEstate(SQLModel, table=True):
    search_event_id: Optional[int] = Field(
        default=None, foreign_key="searchevent.id", primary_key=True
    )
    estate_id: Optional[int] = Field(
        default=None, foreign_key="estate.id", primary_key=True
    )


class SearchEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    estates: List["Estate"] = Relationship(
        back_populates="search_events", link_model=SearchEventEstate
    )
    search_id: Optional[int] = Field(default=None, foreign_key="search.id")
    search: Optional["Search"] = Relationship(back_populates="search_events")
    prices: List["Price"] = Relationship(back_populates="search_event")

class Search(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="searches")
    location: str = Field(index=True)
    distance_radius: int = Field(default=0)
    coordinates: Optional[str] = Field(default=None)
    from_price: Optional[int]
    to_price: Optional[int]
    from_surface: Optional[int]
    to_surface: Optional[int]
    search_events: List["SearchEvent"] = Relationship(back_populates="search")
    users: List[User] = Relationship(back_populates="searches", link_model=SearchUser)
"""
CATEGORY_MAP = {"terrain": "Plot"}


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

    # TODO handle missing category
    category = (await session.execute(cat_query)).first()

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
    session.add_all([Search, SearchEvent])
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
