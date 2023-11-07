import json

import fakeredis
import httpx
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

import api.utils.fetching
from api.models.category import Category
from api.models.price import Price
from api.models.search_event import SearchEvent
from api.settings import settings
from api.utils.search_event import (
    get_search_event_prices,
    get_search_event_by_id,
    get_search_event_avg_stats,
    get_search_event_min_prices,
)
from api.utils.url_parsing import parse_url
from api.models.estate import Estate
from api.models.search import Search

from .conftest import examples, MockAioJSONResponse


def test_parsing_url() -> None:
    input_url = (
        f"{settings.base_url}pl/wyniki/sprzedaz/dzialka/wielkopolskie/"
        f"poznan/poznan/poznan?ownerTypeSingleSelect=ALL&distanceRadius=0"
        f"&priceMin=100000&priceMax=200000&viewType=listing"
    )
    output_url = parse_url(input_url)
    output_url = output_url.format(api_key="API_KEY")
    assert output_url == (
        f"{settings.base_url}_next/data/API_KEY/pl/wyniki/sprzedaz/dzialka/"
        f"wielkopolskie/poznan/poznan/poznan.json?ownerTypeSingleSelect=ALL&"
        f"distanceRadius=0&priceMin=100000&priceMax=200000&viewType=listing&"
        f"searchingCriteria=sprzedaz&searchingCriteria=dzialka&"
        f"searchingCriteria=wielkopolskie&searchingCriteria=poznan&"
        f"searchingCriteria=poznan&searchingCriteria=poznan"
    )


def test_extracting_token(mocker: MockerFixture) -> None:
    with open("tests/example_files/404_resp.html", "r") as f:
        body = f.read()
    cache = fakeredis.FakeRedis(decode_responses=True)  # type:ignore
    mocker.patch("api.utils.fetching.cache", cache)

    api.utils.fetching.extract_token(body)
    assert cache.get("token") == "U-X80D14b5VUVY_qgIbBQ"


@pytest.mark.asyncio
async def test_get_search_event_prices(
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
    search_event = (await _db_session.exec(select(SearchEvent))).first()
    parsed_prices = (
        await _db_session.exec(select(Price).options(selectinload(Price.estate)))
    ).all()
    prices = await get_search_event_prices(_db_session, search_event)
    assert prices == parsed_prices


@pytest.mark.asyncio
async def test_get_search_event_by_id(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    estate = Estate(**examples["estate"])
    search = Search(**examples["search"])
    price = Price(**examples["price"], estate=estate)
    search_event = SearchEvent(estates=[estate], search=search, prices=[price])
    _db_session.add(search_event)
    await _db_session.commit()
    from_db: SearchEvent | None = (
        await _db_session.execute(select(SearchEvent))
    ).scalar()
    assert await get_search_event_by_id(_db_session, from_db.id + 1) is None
    assert await get_search_event_by_id(_db_session, from_db.id) == from_db


@pytest.mark.asyncio
async def test_get_search_event_avg_stats(
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
    search_event = (
        await _db_session.exec(
            select(SearchEvent).options(selectinload(SearchEvent.prices))
        )
    ).first()
    avg_stats = get_search_event_avg_stats(search_event.prices)
    expected_output = {
        "avg_area_in_square_meters": 1075.25,
        "avg_price": 132315.72,
        "avg_price_per_square_meter": 158.67,
        "avg_terrain_area_in_square_meters": None,
    }
    assert avg_stats == expected_output


@pytest.mark.asyncio
async def test_get_search_event_min_prices(
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
    search_event = (
        await _db_session.exec(
            select(SearchEvent).options(selectinload(SearchEvent.prices))
        )
    ).first()
    min_prices_without_top_x = get_search_event_min_prices(search_event.prices)
    assert min_prices_without_top_x == "test"
