from datetime import datetime
from typing import Any, Optional

from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.search import Search
from api.models.search_event import SearchEvent
from api.types.event_stats import EventStatsType
from api.utils.search_event import (
    get_search_event_avg_stats,
    get_search_event_min_prices,
    get_search_event_prices,
)


async def get_search_by_id(session: AsyncSession, id: int) -> Optional["Search"]:
    return (
        await session.exec(
            select(Search)
            .where(Search.id == id)
            .options(selectinload(Search.category))  # type: ignore
        )
    ).first()


async def get_search_events_for_search(
    session: AsyncSession,
    search: Search,
    date_from: datetime,
    date_to: datetime,
) -> list["EventStatsType"]:
    search_events: list[Any] = (
        await session.exec(
            select(SearchEvent).where(  # type: ignore
                and_(
                    SearchEvent.search_id == search.id,
                    SearchEvent.date >= date_from,
                    SearchEvent.date <= date_to,
                )
            )
        )
    ).all()
    events = []
    for event in search_events:
        prices = await get_search_event_prices(session, event)
        if len(prices) == 0:
            continue
        stats = get_search_event_avg_stats(prices)
        stats.update(get_search_event_min_prices(prices))
        events.append(EventStatsType(**stats))  # type: ignore
    return events


def get_search_stats(search_events: list[EventStatsType]) -> dict[str, Any]:
    events_num = len(search_events)
    stats = {
        "avg_price_total": round(
            sum((e.avg_price for e in search_events)) / events_num, 2
        ),
        "avg_price_per_square_meter_total": round(
            sum((e.avg_price_per_square_meter for e in search_events)) / events_num, 2
        ),
    }
    area_in_square_meters_sum = sum(
        (
            e.avg_area_in_square_meters
            for e in search_events
            if e.avg_area_in_square_meters
        )
    )
    terrain_area_in_square_meters_sum = sum(
        (
            e.avg_terrain_area_in_square_meters
            for e in search_events
            if e.avg_terrain_area_in_square_meters
        )
    )
    avg_area_in_square_meters = (
        round(area_in_square_meters_sum / events_num, 2)
        if area_in_square_meters_sum
        else None
    )
    avg_terrain_area_in_square_meters = (
        round(terrain_area_in_square_meters_sum / events_num, 2)
        if terrain_area_in_square_meters_sum
        else None
    )
    stats["avg_area_total"] = avg_area_in_square_meters  # type: ignore
    stats["avg_terrain_total"] = avg_terrain_area_in_square_meters  # type: ignore
    return stats
