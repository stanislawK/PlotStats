from typing import Any

import strawberry
from strawberry.types import Info

from api.types.event_stats import (
    EventStatsInput,
    EventStatsType,
    GetSearchEventStatsResponse,
    NoPricesFoundError,
    SearchEventDoesntExistError,
)
from api.utils.search_event import (
    get_search_event_avg_stats,
    get_search_event_by_id,
    get_search_event_min_prices,
    get_search_event_prices,
)


@strawberry.type
class Query:
    @strawberry.field
    async def search_event_stats(
        self, info: Info[Any, Any], input: EventStatsInput
    ) -> GetSearchEventStatsResponse:
        session = info.context["session"]
        search_event = await get_search_event_by_id(session, input.id)
        if not search_event:
            return SearchEventDoesntExistError()
        prices = await get_search_event_prices(session, search_event)
        if len(prices) == 0:
            return NoPricesFoundError()
        stats = get_search_event_avg_stats(prices)
        stats.update(get_search_event_min_prices(prices, input.top_prices))
        return EventStatsType(**stats)  # type: ignore
