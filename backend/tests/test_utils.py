import json
from datetime import datetime, timedelta

import fakeredis
import httpx
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

import api.utils.fetching
import api.utils.jwt as jwt_utils
import api.utils.user as user_utils
from api.models.category import Category
from api.models.estate import Estate
from api.models.price import Price
from api.models.scan_failure import ScanFailure
from api.models.search import Search, encode_url
from api.models.search_event import SearchEvent
from api.models.user import User
from api.settings import settings
from api.utils.search import (
    get_last_failures,
    get_last_successes,
    get_search_events_for_search,
    get_search_id_by_url,
    get_search_stats,
)
from api.utils.search_event import (
    get_search_event_avg_stats,
    get_search_event_by_id,
    get_search_event_min_prices,
    get_search_event_prices,
)
from api.utils.url_parsing import parse_url

from .conftest import MockAioJSONResponse, examples

# mypy: ignore-errors


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
    await authenticated_client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()
    parsed_prices = (
        await _db_session.exec(select(Price).options(selectinload(Price.estate)))
    ).all()
    prices = await get_search_event_prices(_db_session, search_event)
    assert prices == parsed_prices


@pytest.mark.asyncio
async def test_get_search_event_by_id(
    authenticated_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    estate = Estate(**examples["estate"])
    search = Search(**examples["search"])
    price = Price(**examples["price"], estate=estate)
    search_event = SearchEvent(estates=[estate], search=search, prices=[price])
    _db_session.add(search_event)
    await _db_session.commit()
    from_db: SearchEvent | None = (await _db_session.exec(select(SearchEvent))).first()
    assert await get_search_event_by_id(_db_session, from_db.id + 1) is None
    assert await get_search_event_by_id(_db_session, from_db.id) == from_db


@pytest.mark.asyncio
async def test_get_search_event_avg_stats(
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
    await authenticated_client.post("/graphql", json={"query": mutation})
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
    await authenticated_client.post("/graphql", json={"query": mutation})
    search_event = (
        await _db_session.exec(
            select(SearchEvent).options(selectinload(SearchEvent.prices))
        )
    ).first()
    prices = await get_search_event_prices(_db_session, search_event)
    min_prices_without_top_x = get_search_event_min_prices(prices)
    assert min_prices_without_top_x["min_price"].price == 100000
    assert (
        min_prices_without_top_x["min_price_per_square_meter"].price_per_square_meter
        == 26
    )
    min_prices = get_search_event_min_prices(prices, 3)
    assert (
        len(min_prices["min_prices"])
        == len(min_prices["min_prices_per_square_meter"])
        == 3
    )
    assert [p.price for p in min_prices["min_prices"]] == [100000, 100000, 102960]
    assert [
        p.price_per_square_meter for p in min_prices["min_prices_per_square_meter"]
    ] == [26, 49, 81]


@pytest.mark.asyncio
async def test_search_events_for_search(
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
    await authenticated_client.post("/graphql", json={"query": mutation})
    await authenticated_client.post("/graphql", json={"query": mutation})
    search = (
        await _db_session.exec(select(Search).options(selectinload(Search.category)))
    ).first()  # type: ignore
    events = await get_search_events_for_search(
        _db_session,
        search,
        date_to=datetime.utcnow() + timedelta(hours=1),
        date_from=datetime.utcnow() - timedelta(days=365),
    )  # type: ignore
    stats = get_search_stats(events)
    expected_output = {
        "avg_area_total": 1075.25,
        "avg_price_per_square_meter_total": 158.67,
        "avg_price_total": 132315.72,
        "avg_terrain_total": None,
    }
    assert stats == expected_output


@pytest.mark.asyncio
async def test_authenticate_user_valid_credentials(
    _db_session: AsyncSession, add_user: User
) -> None:
    user = await user_utils.authenticate_user(
        _db_session, examples["user"]["email"], examples["user"]["password"]
    )
    assert isinstance(user, User)
    assert user.email == examples["user"]["email"]


@pytest.mark.asyncio
async def test_authenticate_user_wrong_data(
    _db_session: AsyncSession, add_user: User
) -> None:
    attempt_with_wrong_password = await user_utils.authenticate_user(
        _db_session, examples["user"]["email"], "wrong"
    )
    attempt_with_wrong_email = await user_utils.authenticate_user(
        _db_session, "wrong", examples["user"]["password"]
    )
    assert attempt_with_wrong_password is False
    assert attempt_with_wrong_email is False


def test_create_jwt_token() -> None:
    access_token = jwt_utils.create_jwt_token(
        subject="666", fresh=True, token_type="access"
    )
    refresh_token = jwt_utils.create_jwt_token(
        subject="666", fresh=False, token_type="refresh"
    )
    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)
    access_token_decoded = jwt_utils.decode_jwt_token(access_token)
    refresh_token_decoded = jwt_utils.decode_jwt_token(refresh_token)
    assert access_token_decoded["sub"] == "666"
    assert refresh_token_decoded["sub"] == "666"
    assert access_token_decoded["fresh"] is True
    assert refresh_token_decoded["fresh"] is False
    assert access_token_decoded["type"] == "access"
    assert refresh_token_decoded["type"] == "refresh"


@pytest.mark.asyncio
async def test_get_user_from_token(_db_session: AsyncSession, add_user: User) -> None:
    access_token = jwt_utils.create_jwt_token(
        subject=str(add_user.id), fresh=True, token_type="access"
    )
    user = await jwt_utils.get_user_from_token(access_token, _db_session)
    assert isinstance(user, User)
    assert user.email == add_user.email
    assert user.id == add_user.id


@pytest.mark.asyncio
async def test_get_last_failures(
    _db_session: AsyncSession, add_category: Category
) -> None:
    search_1 = Search(category=add_category, **examples["search"])
    search_2 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "a"},
        }
    )
    failure_1 = ScanFailure(search=search_1, status_code=404)
    failure_2 = ScanFailure(search=search_2, status_code=404)
    failure_3 = ScanFailure(search=search_1, status_code=404)
    _db_session.add_all([search_1, search_2, failure_1, failure_2, failure_3])
    await _db_session.commit()
    _db_session.flush()
    last_failures = await get_last_failures(session=_db_session)
    assert len(last_failures) == 2
    assert search_1.id in last_failures and search_2.id in last_failures
    assert last_failures.get(search_1.id) == failure_3.date


@pytest.mark.asyncio
async def test_get_last_successes(
    _db_session: AsyncSession, add_category: Category
) -> None:
    search_1 = Search(category=add_category, **examples["search"])
    search_2 = Search(
        **{
            **examples["search"],
            **{"category": add_category, "url": examples["search"]["url"] + "a"},
        }
    )
    estate = Estate(**examples["estate"])
    price = Price(**examples["price"], estate=estate)
    success_1 = SearchEvent(estates=[estate], search=search_1, prices=[price])
    success_2 = SearchEvent(estates=[estate], search=search_2, prices=[price])
    success_3 = SearchEvent(estates=[estate], search=search_1, prices=[price])
    _db_session.add_all([search_1, search_2, success_1, success_2, success_3])
    await _db_session.commit()
    _db_session.flush()
    last_successes = await get_last_successes(session=_db_session)
    assert len(last_successes) == 2
    assert search_1.id in last_successes and search_2.id in last_successes
    assert last_successes.get(search_1.id) == success_3.date


@pytest.mark.asyncio
async def test_get_search_id_by_url(
    _db_session: AsyncSession, add_category: Category
) -> None:
    search_data = examples["search"].copy()
    url = search_data.pop("url")
    encoded_url = encode_url(url)
    search_1 = Search.model_validate(
        Search(category=add_category, url=encoded_url, **search_data)
    )
    _db_session.add(search_1)
    await _db_session.commit()
    _db_session.flush()
    id = await get_search_id_by_url(session=_db_session, url=url)
    assert id == search_1.id
