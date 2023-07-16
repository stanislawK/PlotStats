from api.models import Search, Estate, Price
import jmespath
import json

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
# TODO from_surface i to_surface
# Search.coordinates
with open("body.json", "r") as f:
    body = json.load(f)
coordinates_org = jmespath.search("pageProps.mapBoundingBox.boundingBox", body)
coordinates_alt = jmespath.search("pageProps.data.searchMapPins.boundingBox", body)


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


category_map = {"terrain": "Plot"}
category = jmespath.search("pageProps.estate", body)

# Search.distance_radius
distance_radius = jmespath.search("pageProps.filteringQueryParams.distanceRadius", body)

# Search.from_price
from_price = jmespath.search("pageProps.filteringQueryParams.priceMin", body)

# Search.to_price
to_price = jmespath.search("pageProps.filteringQueryParams.priceMax", body)

# Search.location
location = jmespath.search("pageProps.filteringQueryParams.locations[0]", body)

search = Search(
    location=location,
    distance_radius=distance_radius,
    coordinates=parse_coordinates(coordinates_org, coordinates_alt),
    from_price=from_price,
    to_price=to_price,
)

ads = jmespath.search("pageProps.data.searchAds.items", body)
for ad in ads:
    date_created = jmespath.search()
    estate = Estate(
        id=ad.get("id"),
        title=ad.get("title", ""),
        street=jmespath.search("location.address.street.name", ad),
        city=jmespath.search("location.address.city.name", ad),
        province=jmespath.search("location.address.province.name", ad),
        location=jmespath.search("locationLabel.value", ad),
        date_created=ad.get("dateCreatedFirst") or ad.get("dateCreated"),
        url=ad.get("slug"),
    )
    price = Price(
        price=jmespath.search("totalPrice.value", ad),
        price_per_square_meter=jmespath.search("pricePerSquareMeter.value", ad),
        area_in_square_meters=ad.get("areaInSquareMeters"),
        terrain_area_in_square_meters=ad.get("terrainAreaInSquareMeters"),
        estate_id=ad.get("id"),
    )
