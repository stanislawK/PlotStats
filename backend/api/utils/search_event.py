from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.price import Price
from api.models.search_event import SearchEvent


async def get_search_event_prices(
    session: AsyncSession, search_event: "SearchEvent"
) -> list["Price"]:
    prices = (
        await session.exec(
            select(Price)
            .where(Price.search_event_id == search_event.id)
            .options(selectinload(Price.estate))
        )
    ).all()
    return prices


async def get_search_event_by_id(
    session: AsyncSession, search_event_id: int
) -> "SearchEvent":
    return (
        await session.exec(select(SearchEvent).where(SearchEvent.id == search_event_id))
    ).first()


def get_search_event_avg_stats(prices: list["Price"]) -> dict[str, Optional[float]]:
    num_of_prices: int = len(prices)
    stats = {
        "avg_price": round(sum((p.price for p in prices)) / num_of_prices, 2),
        "avg_price_per_square_meter": round(
            sum((p.price_per_square_meter for p in prices)) / len(prices), 2
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
    stats["avg_area_in_square_meters"] = avg_area_in_square_meters
    stats["avg_terrain_area_in_square_meters"] = avg_terrain_area_in_square_meters
    return stats


def get_search_event_min_prices(
    prices: list["Price"], top_prices: Optional[int] = None
) -> list["Price"]:
    stats = dict()
    import pdb

    pdb.set_trace()
    sorted_by_price = sorted(prices, key=lambda p: p.price)
    stats["min_price"] = sorted_by_price[0]
    sorted_by_price_per_square_meter = sorted(
        prices, key=lambda p: p.price_per_square_meter
    )
    stats["min_price_per_square_meter"] = sorted_by_price_per_square_meter[0]
    if top_prices and top_prices > 0:
        stats["min_prices"] = sorted_by_price[:top_prices]
        stats["min_prices_per_square_meter"] = sorted_by_price_per_square_meter[
            :top_prices
        ]
    return stats
