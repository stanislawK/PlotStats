import json
from datetime import datetime, timedelta

import httpx
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.category import Category
from api.models.estate import Estate
from api.models.price import Price
from api.models.scan_failure import ScanFailure
from api.models.search import Search
from api.models.search_event import SearchEvent
from api.types.category import CategoryType
from api.types.event_stats import EventStatsType
from api.types.price import convert_price_from_db
from api.types.scan import AdhocScanInput, PydanticAdhocScanInput
from api.types.search_stats import (
    convert_search_fail_rate,
    convert_search_stats_from_db,
    get_last_statuses,
)
from api.utils.search_event import get_search_event_prices

from .conftest import MockCffiJSONResponse, examples

# mypy: ignore-errors


def test_category_type() -> None:
    [name_field] = CategoryType.__strawberry_definition__.fields

    assert name_field.python_name == "name"

    instance = Category(name="Plot")
    data = CategoryType.from_pydantic(instance)
    assert data.name == "Plot"  # type: ignore


def test_adhoc_scan_input_type() -> None:
    [url_field, schedule_field] = AdhocScanInput.__strawberry_definition__.fields

    assert url_field.python_name == "url"
    assert schedule_field.python_name == "schedule"
    with pytest.raises(
        ValidationError,
        match=("Input should be a valid URL"),
    ):
        PydanticAdhocScanInput(url="test")
    with pytest.raises(
        ValidationError,
        match=("url has to contain base url"),
    ):
        PydanticAdhocScanInput(url="https://test.com")
    with pytest.raises(
        ValidationError,
        match=("schedule.day_of_week\\n  Field required"),  # noqa
    ):
        PydanticAdhocScanInput(
            url="https://www.test.io/query_params", schedule={"hour": 1}
        )
    instance = PydanticAdhocScanInput(
        url="https://www.test.io/query_params",
        schedule={"day_of_week": 0, "hour": 1, "minute": 2},
    )
    data = AdhocScanInput.from_pydantic(instance)
    assert data.url.unicode_string() == "https://www.test.io/query_params"
    assert data.schedule.hour == 1  # type: ignore
    assert data.schedule.minute == 2  # type: ignore
    assert data.schedule.day_of_week == 0  # type: ignore


@pytest.mark.asyncio
async def test_event_stats_type(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockCffiJSONResponse(body, 200)
    mocker.patch("curl_cffi.requests.Session.get", return_value=resp)
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
    await authenticated_client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()  # type: ignore
    prices = await get_search_event_prices(_db_session, search_event)  # type: ignore

    price = prices[0]
    event_stats = EventStatsType(
        id=1,
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
        if estate_key == "url":
            assert (
                "https://www.test.io/pl/oferta/" + getattr(price.estate, estate_key)
                == estate_value
            )
            continue
        assert getattr(price.estate, estate_key) == estate_value


@pytest.mark.asyncio
async def test_search_stats_type(
    authenticated_client: httpx.AsyncClient,
    _db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockCffiJSONResponse(body, 200)
    mocker.patch("curl_cffi.requests.Session.get", return_value=resp)
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
    await authenticated_client.post("/graphql", json={"query": mutation})
    await authenticated_client.post("/graphql", json={"query": mutation})
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


@pytest.mark.asyncio
async def test_get_last_statuses(
    _db_session: AsyncSession, add_category: Category
) -> None:
    search_1 = Search(category=add_category, **examples["search"])
    search_2 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "a"},
        }
    )
    search_3 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "b"},
        }
    )
    search_4 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "c"},
        }
    )
    search_5 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "d"},
        }
    )
    estate = Estate(**examples["estate"])
    price = Price(**examples["price"], estate=estate)
    failure_1 = ScanFailure(search=search_2, status_code=404)
    success_1 = SearchEvent(estates=[estate], search=search_3, prices=[price])
    failure_2 = ScanFailure(search=search_4, status_code=404)
    success_2 = SearchEvent(estates=[estate], search=search_4, prices=[price])
    success_3 = SearchEvent(estates=[estate], search=search_5, prices=[price])
    failure_3 = ScanFailure(search=search_5, status_code=404)
    _db_session.add_all(
        [
            search_1,
            search_2,
            search_3,
            search_4,
            search_5,
            failure_1,
            success_1,
            failure_2,
            success_2,
            success_3,
            failure_3,
        ]
    )
    await _db_session.commit()
    _db_session.flush()
    last_statuses = await get_last_statuses(session=_db_session)
    expected = {
        search_1.id: "unknown",
        search_2.id: "failed",
        search_3.id: "success",
        search_4.id: "success",
        search_5.id: "failed",
    }
    statuses = last_statuses.statuses
    assert len(statuses) == len(expected.keys())
    for status in statuses:
        assert expected.get(status.id) == status.status


@pytest.mark.asyncio
async def test_get_search_fail_rate(
    _db_session: AsyncSession, add_category: Category
) -> None:
    past_date = datetime.today() - timedelta(days=15)
    out_of_scope = datetime.today() - timedelta(days=32)
    search_1 = Search(category=add_category, **examples["search"])
    estate = Estate(**examples["estate"])
    price = Price(**examples["price"], estate=estate)
    failure_1 = ScanFailure(search=search_1, status_code=404)
    failure_2 = ScanFailure(search=search_1, status_code=403, date=past_date)
    failure_3 = ScanFailure(search=search_1, status_code=404, date=out_of_scope)
    success_1 = SearchEvent(estates=[estate], search=search_1, prices=[price])
    success_2 = SearchEvent(
        estates=[estate], search=search_1, prices=[price], date=past_date
    )
    success_3 = SearchEvent(
        estates=[estate], search=search_1, prices=[price], date=out_of_scope
    )
    _db_session.add_all(
        [
            search_1,
            failure_1,
            failure_2,
            failure_3,
            estate,
            price,
            success_1,
            success_2,
            success_3,
        ]
    )
    await _db_session.commit()
    _db_session.flush()
    fail_rate = await convert_search_fail_rate(session=_db_session, days=30)
    successes = fail_rate.successes
    failures = fail_rate.failures
    assert len(successes) == 1 and len(failures) == 1
    assert (
        successes[0].search_id == search_1.id and failures[0].search_id == search_1.id
    )
    assert len(successes[0].successes) == 2
    assert len(failures[0].failures) == 2
