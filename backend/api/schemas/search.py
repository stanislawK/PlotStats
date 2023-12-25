from datetime import datetime, timedelta
from typing import Any

import strawberry
from strawberry.types import Info

from api.permissions import IsAuthenticated
from api.types.search_stats import (
    GetSearchStatsResponse,
    SearchDoesntExistError,
    SearchStatsInput,
    convert_search_stats_from_db,
)
from api.utils.search import get_search_by_id


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])  # type: ignore
    async def search_stats(
        self, info: Info[Any, Any], input: SearchStatsInput
    ) -> GetSearchStatsResponse:
        session = info.context["session"]
        search = await get_search_by_id(session, input.id)
        if not search:
            return SearchDoesntExistError()
        date_from = input.date_from or datetime.utcnow() - timedelta(days=365)
        date_to = input.date_to or datetime.utcnow()
        return await convert_search_stats_from_db(session, search, date_from, date_to)
