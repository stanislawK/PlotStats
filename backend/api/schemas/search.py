from datetime import datetime, timedelta
from typing import Any

import strawberry
from strawberry.types import Info

from api.permissions import IsAuthenticated
from api.types.event_stats import EventStatsType
from api.types.search_stats import (
    AssignSearchInput,
    AssignSearchResponse,
    FavoriteSearchDoesntExistError,
    GetSearchesResponse,
    GetSearchEventsStatsResponse,
    GetSearchStatsResponse,
    NoSearchesAvailableError,
    NoSearchEventError,
    SearchAssignSuccessfully,
    SearchDoesntExistError,
    SearchEventsStatsType,
    SearchStatsInput,
    convert_search_stats_from_db,
    convert_searches_from_db,
)
from api.utils.search import get_search_by_id, get_searches
from api.utils.search_event import (
    get_search_event_avg_stats,
    get_search_event_min_prices,
    get_search_event_prices,
)
from api.utils.user import add_favorite_search


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def search_stats(
        self, info: Info[Any, Any], input: SearchStatsInput
    ) -> GetSearchStatsResponse:
        session = info.context["session"]
        user = info.context["request"].state.user
        search_id = input.id or user.favorite_search_id
        if not search_id:
            return SearchDoesntExistError()
        search = await get_search_by_id(session, search_id)
        if not search:
            return SearchDoesntExistError()
        date_from = input.date_from or datetime.utcnow() - timedelta(days=365)
        date_to = input.date_to or datetime.utcnow()
        return await convert_search_stats_from_db(session, search, date_from, date_to)

    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def all_searches(self, info: Info[Any, Any]) -> GetSearchesResponse:
        session = info.context["session"]
        searches_db = await get_searches(session=session)
        if len(searches_db) == 0:
            return NoSearchesAvailableError()
        return convert_searches_from_db(searches_db)

    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def users_searches(self, info: Info[Any, Any]) -> GetSearchesResponse:
        session = info.context["session"]
        user = info.context["request"].state.user
        searches_db = await get_searches(session=session, user_id=user.id)
        if len(searches_db) == 0:
            return NoSearchesAvailableError()
        return convert_searches_from_db(searches_db)

    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def search_events_stats(
        self, info: Info[Any, Any]
    ) -> GetSearchEventsStatsResponse:
        session = info.context["session"]
        user = info.context["request"].state.user
        if not user.favorite_search_id:
            return FavoriteSearchDoesntExistError()
        search = await get_search_by_id(
            session, user.favorite_search_id, with_events=True
        )
        if not search or len(search.search_events) == 0:
            return NoSearchEventError()
        search_event_stats = []
        for search_event in search.search_events:
            prices = await get_search_event_prices(session, search_event)
            if len(prices) == 0:
                continue
            stats = get_search_event_avg_stats(prices)
            stats.update(get_search_event_min_prices(prices))
            stats["date"] = search_event.date  # type: ignore
            stats["id"] = search_event.id
            search_event_stats.append(EventStatsType(**stats))  # type: ignore
        return SearchEventsStatsType(search_events=search_event_stats)


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])  # type: ignore
    async def assign_search_to_user(
        self, info: Info[Any, Any], input: AssignSearchInput
    ) -> AssignSearchResponse:
        session = info.context["session"]
        search = await get_search_by_id(session, input.id)
        if not search:
            return SearchDoesntExistError()
        user = info.context["request"].state.user
        if user not in search.users:
            search.users.append(user)
            session.add(search)
            await session.commit()
        return SearchAssignSuccessfully()

    @strawberry.mutation(permission_classes=[IsAuthenticated])  # type: ignore
    async def assign_favorite_search_to_user(
        self, info: Info[Any, Any], input: AssignSearchInput
    ) -> AssignSearchResponse:
        session = info.context["session"]
        search = await get_search_by_id(session, input.id)
        if not search:
            return SearchDoesntExistError()
        user = info.context["request"].state.user
        if isinstance(search.id, int) and user.favorite_search_id != search.id:
            await add_favorite_search(session, user, search.id)
        return SearchAssignSuccessfully()
