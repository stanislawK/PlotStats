import json
from datetime import datetime, timedelta

import httpx
import pytest
from pydantic.error_wrappers import ValidationError
from pytest_mock import MockerFixture
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.category import Category
from api.models.search import Search
from api.models.search_event import SearchEvent
from api.types.category import CategoryType
from api.types.event_stats import EventStatsType
from api.types.price import convert_price_from_db
from api.types.scan import AdhocScanInput, PydanticAdhocScanInput
from api.types.search_stats import convert_search_stats_from_db
from api.utils.search_event import get_search_event_prices

from .conftest import MockAioJSONResponse

# mypy: ignore-errors


def test_category_type() -> None:
    [name_field] = CategoryType._type_definition.fields  # type: ignore

    assert name_field.python_name == "name"

    instance = Category(name="Plot")
    data = CategoryType.from_pydantic(instance)
    assert data.name == "Plot"  # type: ignore


def test_adhoc_scan_input_type() -> None:
    [url_field, schedule_field] = AdhocScanInput._type_definition.fields  # type: ignore

    assert url_field.python_name == "url"
    assert schedule_field.python_name == "schedule"
    with pytest.raises(
        ValidationError,
        match=("invalid or missing URL scheme"),
    ):
        PydanticAdhocScanInput(url="test")
    with pytest.raises(
        ValidationError,
        match=("url has to contain base url"),
    ):
        PydanticAdhocScanInput(url="https://test.com")
    with pytest.raises(
        ValidationError,
        match=(
            "day_of_week\\n  field required \(type=value_error\.missing\)\\nschedule -> minute\\n  field required \(type=value_error\.missing\)"  # noqa
        ),
    ):
        PydanticAdhocScanInput(
            url="https://www.test.io/query_params", schedule={"hour": 1}
        )
    instance = PydanticAdhocScanInput(
        url="https://www.test.io/query_params",
        schedule={"day_of_week": 0, "hour": 1, "minute": 2},
    )
    data = AdhocScanInput.from_pydantic(instance)
    assert data.url == "https://www.test.io/query_params"
    assert data.schedule.hour == 1  # type: ignore
    assert data.schedule.minute == 2  # type: ignore
    assert data.schedule.day_of_week == 0  # type: ignore


@pytest.mark.asyncio
async def test_event_stats_type(
    client: httpx.AsyncClient, _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
                ... on ScanFailedError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    await client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()  # type: ignore
    prices = await get_search_event_prices(_db_session, search_event)  # type: ignore
    price = prices[0]
    event_stats = EventStatsType(
        avg_price=55.55,
        avg_price_per_square_meter=55.55,
        avg_terrain_area_in_square_meters=999.99,
        avg_area_in_square_meters=999.99,
        min_price=convert_price_from_db(price),
        min_price_per_square_meter=convert_price_from_db(price),
        min_prices=[convert_price_from_db(price)],
        min_prices_per_square_meter=[convert_price_from_db(price)],
    )
    for key, value in event_stats.min_price.__dict__.items():
        if key == "estate":
            continue
        assert getattr(price, key) == value

    for estate_key, estate_value in event_stats.min_price.estate.__dict__.items():
        assert getattr(price.estate, estate_key) == estate_value


@pytest.mark.asyncio
async def test_search_stats_type(
    client: httpx.AsyncClient, _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}"
                }}) {{
                __typename
                ... on ScanSucceeded {{
                    message
                }}
                ... on ScanFailedError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    await client.post("/graphql", json={"query": mutation})
    await client.post("/graphql", json={"query": mutation})
    search = (
        await _db_session.exec(select(Search).options(selectinload(Search.category)))
    ).first()  # type: ignore
    search_stats = await convert_search_stats_from_db(
        _db_session,
        search,
        date_from=datetime.utcnow() - timedelta(days=365),
        date_to=datetime.utcnow() + timedelta(days=1),
    )
    search_events_db = (
        await _db_session.exec(
            select(SearchEvent).where(SearchEvent.search_id == search.id)
        )
    ).all()
    assert len(search_stats.events) == len(search_events_db)
    assert search_stats.category.name == "Plot"
