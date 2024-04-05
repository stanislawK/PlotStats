from datetime import datetime, timedelta
from typing import Any

import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from api.models.search import decode_url
from api.permissions import IsAuthenticated
from api.schedulers import remove_scan_periodic_task, setup_scan_periodic_task
from api.types.event_stats import EventStatsType
from api.types.general import InputValidationError
from api.types.search_stats import (
    AssignSearchInput,
    AssignSearchResponse,
    DaysOutOfRangeError,
    EditScheduleInput,
    EditScheduleResponse,
    FavoriteSearchDoesntExistError,
    GetSearchesResponse,
    GetSearchEventsStatsResponse,
    GetSearchStatsResponse,
    NoSearchesAvailableError,
    NoSearchEventError,
    ScheduleEditedSuccessfully,
    SearchAssignSuccessfully,
    SearchDoesntExistError,
    SearchesStatusType,
    SearchEventsStatsInput,
    SearchEventsStatsType,
    SearchFailRateInput,
    SearchFailRateResponse,
    SearchStatsInput,
    convert_search_fail_rate,
    convert_search_stats_from_db,
    convert_searches_from_db,
    get_last_statuses,
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
        parsed_searches = convert_searches_from_db(searches_db)
        parsed_searches.favorite_id = user.favorite_search_id
        return parsed_searches

    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def search_events_stats(
        self, info: Info[Any, Any], input: SearchEventsStatsInput
    ) -> GetSearchEventsStatsResponse:
        session = info.context["session"]
        if not (search_id := input.id):
            user = info.context["request"].state.user
            if not isinstance(user.favorite_search_id, int):
                return FavoriteSearchDoesntExistError()
            search_id = user.favorite_search_id
        search = await get_search_by_id(session, search_id, with_events=True)
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

    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def searches_last_status(self, info: Info[Any, Any]) -> SearchesStatusType:
        session = info.context["session"]
        return await get_last_statuses(session=session)

    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def search_fail_rate(
        self, info: Info[Any, Any], input: SearchFailRateInput
    ) -> SearchFailRateResponse:
        if input.days > 180:
            return DaysOutOfRangeError()
        session = info.context["session"]
        return await convert_search_fail_rate(session, input.days)


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

    @strawberry.mutation(permission_classes=[IsAuthenticated])  # type: ignore
    async def edit_schedule(
        self, info: Info[Any, Any], input: EditScheduleInput
    ) -> EditScheduleResponse:
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        session = info.context["session"]
        search = await get_search_by_id(session, data.id)
        if not search:
            return SearchDoesntExistError()
        decoded_url = decode_url(search.url)  # type: ignore
        if schedule := data.schedule:
            schedule_dict = schedule.__dict__
            search.schedule = schedule_dict
            setup_scan_periodic_task(
                decoded_url, schedule_dict, search.id  # type: ignore
            )
        else:
            search.schedule = None
            remove_scan_periodic_task(decoded_url)
        session.add(search)
        await session.commit()
        return ScheduleEditedSuccessfully()
