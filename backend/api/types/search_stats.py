from datetime import datetime, timedelta
from typing import Annotated, List, Optional, Union

import strawberry
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from strawberry import LazyType

from api.models.search import Search, decode_url
from api.types.category import CategoryType, convert_category_from_db
from api.types.event_stats import EventStatsType, NoPricesFoundError
from api.types.general import Error, InputValidationError
from api.types.scan import PydanticScanSchedule, ScanSchedule
from api.utils.search import get_search_events_for_search, get_search_stats


@strawberry.input
class SearchStatsInput:
    id: Optional[int] = strawberry.UNSET
    date_from: Optional[datetime] = strawberry.UNSET
    date_to: Optional[datetime] = strawberry.UNSET


class PydanticEditScheduleInput(BaseModel):
    id: int
    schedule: Optional[PydanticScanSchedule] = None


@strawberry.input
class AssignSearchInput:
    id: int


@strawberry.experimental.pydantic.input(model=PydanticEditScheduleInput)
class EditScheduleInput:
    id: strawberry.auto
    schedule: Optional[LazyType["ScanSchedule", __name__]]


@strawberry.input
class SearchEventsStatsInput:
    id: Optional[int] = strawberry.UNSET


@strawberry.experimental.pydantic.type(Search)
class SearchStatsType:
    id: strawberry.auto
    date_from: datetime
    date_to: datetime
    category: CategoryType
    location: strawberry.auto
    distance_radius: strawberry.auto
    from_price: strawberry.auto
    to_price: strawberry.auto
    from_surface: strawberry.auto
    to_surface: strawberry.auto
    avg_price_total: float
    avg_price_per_square_meter_total: float
    avg_area_total: Optional[float] = strawberry.UNSET
    avg_terrain_total: Optional[float] = strawberry.UNSET
    events: List[EventStatsType]


@strawberry.experimental.pydantic.type(PydanticScanSchedule, all_fields=True)
class ScheduleType:
    pass


@strawberry.experimental.pydantic.type(Search)
class SearchType:
    id: strawberry.auto
    category: CategoryType
    location: strawberry.auto
    distance_radius: strawberry.auto
    coordinates: strawberry.auto
    from_price: strawberry.auto
    to_price: strawberry.auto
    from_surface: strawberry.auto
    to_surface: strawberry.auto
    url: strawberry.auto
    schedule: Optional[ScheduleType] = None


@strawberry.type
class SearchesType:
    searches: List[SearchType]
    favorite_id: Optional[int] = None


@strawberry.type
class SearchEventsStatsType:
    search_events: List[EventStatsType]


async def convert_search_stats_from_db(
    session: AsyncSession,
    search: Search,
    date_from: datetime = datetime.utcnow() - timedelta(days=365),
    date_to: datetime = datetime.utcnow(),
) -> SearchStatsType:
    search_events = await get_search_events_for_search(
        session=session, search=search, date_from=date_from, date_to=date_to
    )
    search_stats = get_search_stats(search_events)
    return SearchStatsType(
        id=search.id,
        date_from=date_from,
        date_to=date_to,
        category=convert_category_from_db(search.category),  # type: ignore
        location=search.location,
        distance_radius=search.distance_radius,
        from_price=search.from_price,
        to_price=search.to_price,
        from_surface=search.from_surface,
        to_surface=search.to_surface,
        avg_price_total=search_stats.get("avg_price_total"),
        avg_price_per_square_meter_total=search_stats.get(
            "avg_price_per_square_meter_total"
        ),
        avg_area_total=search_stats.get("avg_area_total"),
        avg_terrain_total=search_stats.get("avg_terrain_total"),
        events=search_events,
    )


def convert_searches_from_db(
    searches: list[Search],
) -> SearchesType:
    converted = []
    for search in searches:
        if isinstance(search.schedule, dict):
            schedule = ScheduleType(**search.schedule)
        else:
            schedule = None
        converted.append(
            SearchType(
                id=search.id,
                category=convert_category_from_db(search.category),  # type: ignore
                location=search.location,
                distance_radius=search.distance_radius,
                coordinates=search.coordinates,
                from_price=search.from_price,
                to_price=search.to_price,
                from_surface=search.from_surface,
                to_surface=search.to_surface,
                url=decode_url(search.url),  # type: ignore
                schedule=schedule,
            )
        )
    return SearchesType(searches=converted)


@strawberry.type
class FavoriteSearchDoesntExistError(Error):
    message: str = "Select your favorite search first"


@strawberry.type
class NoSearchEventError(Error):
    message: str = "There are no events for search"


@strawberry.type
class SearchDoesntExistError(Error):
    message: str = "Search with provided id doesn't exist"


@strawberry.type
class NoSearchesAvailableError(Error):
    message: str = "No searches available"


@strawberry.type
class SearchAssignSuccessfully:
    message: str = "Search assigned successfully"


@strawberry.type
class ScheduleEditedSuccessfully:
    message: str = "Schedule edited successfully"


GetSearchStatsResponse = Annotated[
    Union[SearchStatsType, SearchDoesntExistError],
    strawberry.union("GetSearchStatsResponse"),
]

GetSearchesResponse = Annotated[
    Union[SearchesType, NoSearchesAvailableError],
    strawberry.union("GetSearchesResponse"),
]

AssignSearchResponse = Annotated[
    Union[SearchAssignSuccessfully, SearchDoesntExistError],
    strawberry.union("AssignSearchResponse"),
]

GetSearchEventsStatsResponse = Annotated[
    Union[
        SearchEventsStatsType,
        FavoriteSearchDoesntExistError,
        NoSearchEventError,
        NoPricesFoundError,
    ],
    strawberry.union("GetSearchEventsStatsResponse"),
]

EditScheduleResponse = Annotated[
    Union[ScheduleEditedSuccessfully, SearchDoesntExistError, InputValidationError],
    strawberry.union("EditScheduleResponse"),
]
