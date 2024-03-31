from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import and_, func
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.scan_failure import ScanFailure
from api.models.search import Search, encode_url
from api.models.search_event import SearchEvent
from api.types.event_stats import EventStatsType
from api.utils.search_event import (
    get_search_event_avg_stats,
    get_search_event_min_prices,
    get_search_event_prices,
)


async def get_search_by_id(
    session: AsyncSession, id: int, with_events: bool = False
) -> Optional["Search"]:
    if with_events:
        return (
            await session.exec(
                select(Search)
                .where(Search.id == id)
                .options(
                    selectinload(Search.category),  # type: ignore
                    selectinload(Search.search_events),  # type: ignore
                )
            )
        ).first()
    return (
        await session.exec(
            select(Search)
            .where(Search.id == id)
            .options(selectinload(Search.category))  # type: ignore
        )
    ).first()


async def get_searches(
    session: AsyncSession, user_id: Optional[int] = None
) -> list["Search"]:
    query = select(Search).options(selectinload(Search.category))  # type: ignore
    if user_id:
        query = query.where(Search.users.any(id=user_id))  # type: ignore
    return [search for search in (await session.exec(query)).all()]


async def get_search_events_for_search(
    session: AsyncSession,
    search: Search,
    date_from: datetime,
    date_to: datetime,
) -> Sequence["EventStatsType"]:
    search_events: Sequence["SearchEvent"] = (
        await session.exec(
            select(SearchEvent).where(
                and_(
                    SearchEvent.search_id == search.id,  # type: ignore
                    SearchEvent.date >= date_from,  # type: ignore
                    SearchEvent.date <= date_to,  # type: ignore
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
        stats["id"] = event.id
        events.append(EventStatsType(**stats))  # type: ignore
    return events


def get_search_stats(search_events: Sequence[EventStatsType]) -> dict[str, Any]:
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


async def get_last_failures(session: AsyncSession) -> dict[int, datetime]:
    query = (
        select(ScanFailure.search_id, func.max(ScanFailure.date).label("last_date"))
        .select_from(ScanFailure)
        .group_by(ScanFailure.search_id)  # type: ignore
    )
    failures = (await session.exec(query)).all()
    return {fail[0]: fail[1] for fail in failures if isinstance(fail[0], int)}


async def get_last_successes(session: AsyncSession) -> dict[int, datetime]:
    query = (
        select(SearchEvent.search_id, func.max(SearchEvent.date).label("last_date"))
        .select_from(SearchEvent)
        .group_by(SearchEvent.search_id)  # type: ignore
    )
    successes = (await session.exec(query)).all()
    return {
        success[0]: success[1] for success in successes if isinstance(success[0], int)
    }


async def get_search_id_by_url(session: AsyncSession, url: str) -> int | None:
    encoded_url = encode_url(url)
    search_query = select(Search.id).where(Search.url == encoded_url.decode("ascii"))
    search_id = (await session.exec(search_query)).first()
    return search_id
