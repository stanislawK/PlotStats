from typing import Any, Optional, Sequence

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.price import Price
from api.models.search_event import SearchEvent
from api.types.price import convert_price_from_db


async def get_search_event_prices(
    session: AsyncSession, search_event: "SearchEvent"
) -> Sequence["Price"]:
    prices: Sequence["Price"] = (
        await session.exec(
            select(Price)
            .where(Price.search_event_id == search_event.id)
            .options(selectinload(Price.estate))  # type: ignore
        )
    ).all()
    return prices


async def get_search_event_by_id(
    session: AsyncSession, search_event_id: int
) -> Optional["SearchEvent"]:
    return (
        await session.exec(select(SearchEvent).where(SearchEvent.id == search_event_id))
    ).first()


def get_search_event_avg_stats(prices: Sequence["Price"]) -> dict[str, Optional[float]]:
    num_of_prices: int = len(prices)
    stats = {
        "avg_price": round(sum((p.price for p in prices)) / num_of_prices, 2),
        "avg_price_per_square_meter": round(
            sum((p.price_per_square_meter for p in prices))  # type: ignore
            / len(prices),
            2,
        ),
    }
    area_in_square_meters_sum = sum(
        (p.area_in_square_meters for p in prices if p.area_in_square_meters)
    )
    terrain_area_in_square_meters_sum = sum(
        (
            p.terrain_area_in_square_meters
            for p in prices
            if p.terrain_area_in_square_meters
        )
    )
    avg_area_in_square_meters = (
        round(area_in_square_meters_sum / num_of_prices, 2)
        if area_in_square_meters_sum
        else None
    )
    avg_terrain_area_in_square_meters = (
        round(terrain_area_in_square_meters_sum / num_of_prices, 2)
        if terrain_area_in_square_meters_sum
        else None
    )
    stats["avg_area_in_square_meters"] = avg_area_in_square_meters  # type: ignore
    stats[
        "avg_terrain_area_in_square_meters"
    ] = avg_terrain_area_in_square_meters  # type: ignore
    stats["number_of_offers"] = num_of_prices
    return stats  # type: ignore


def get_search_event_min_prices(
    prices: Sequence["Price"], top_prices: Optional[int] = None
) -> dict[str, Any]:
    stats = dict()
    sorted_by_price = sorted(prices, key=lambda p: p.price)
    stats["min_price"] = convert_price_from_db(sorted_by_price[0])
    sorted_by_price_per_square_meter = sorted(
        prices, key=lambda p: p.price_per_square_meter  # type: ignore
    )
    stats["min_price_per_square_meter"] = convert_price_from_db(
        sorted_by_price_per_square_meter[0]
    )
    if top_prices and top_prices > 0:
        stats["min_prices"] = [
            convert_price_from_db(p)
            for p in sorted_by_price[:top_prices]  # type: ignore
        ]
        stats["min_prices_per_square_meter"] = [
            convert_price_from_db(p)
            for p in sorted_by_price_per_square_meter[:top_prices]  # type: ignore
        ]
    return stats
