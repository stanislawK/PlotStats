import json

import fakeredis
import httpx
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models import Category
from api.models.estate import Estate
from api.models.price import Price
from api.models.search import Search, decode_url
from api.models.search_event import SearchEvent
from api.models.user import User
from api.types.category import CategoryExistsError
from api.utils.jwt import get_jwt_payload

from .conftest import MockAioJSONResponse, MockAioTextResponse, examples

# mypy: ignore-errors


@pytest.mark.asyncio
async def test_categories_query(
    authenticated_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    category = Category(**examples["category"])
    _db_session.add(category)
    await _db_session.commit()
    query = """
        query MyQuery {
            categories {
                name
            }
        }
    """
    response = await authenticated_client.get("/graphql", params={"query": query})
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]["categories"]) == 1
    assert result["data"]["categories"][0]["name"] == examples["category"]["name"]


@pytest.mark.asyncio
async def test_categories_unauthenticated(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    category = Category(**examples["category"])
    _db_session.add(category)
    await _db_session.commit()
    query = """
        query MyQuery {
            categories {
                name
            }
        }
    """
    response = await client.get("/graphql", params={"query": query})
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_categories_query_fetch_id_should_fail(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    category = Category(**examples["category"])
    _db_session.add(category)
    await _db_session.commit()
    query = """
        query MyQuery {
            categories {
                id
            }
        }
    """
    response = await client.get("/graphql", params={"query": query})
    assert response.status_code == 200
    result = response.json()
    assert result["data"] is None
    assert len(result["errors"]) == 1


@pytest.mark.asyncio
async def test_create_category_mutation(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
                ... on CategoryExistsError {
                    message
                }
            }
        }
    """
    response = await admin_client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryType"
    assert result["data"]["createCategory"]["name"] == "Test2"
    query = select(Category).where(Category.name == "Test2")
    category_db = (await _db_session.execute(query)).scalar()
    assert category_db.name == "Test2"  # type: ignore


@pytest.mark.asyncio
async def test_create_category_mutation_unauthorized(
    client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
            }
        }
    """
    response = await client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_create_category_mutation_non_admin(
    authenticated_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
            }
        }
    """
    response = await authenticated_client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"] is None
    assert result["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.asyncio
async def test_create_category_mutation_duplicate_should_produce_error(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    category = Category(name="Test2")
    _db_session.add(category)
    await _db_session.commit()
    mutation = """
        mutation newCategory {
            createCategory(input: {name: "Test2"}) {
                __typename
                ... on CategoryType {
                    name
                }
                ... on CategoryExistsError {
                    message
                }
            }
        }
    """
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryExistsError"
    err = CategoryExistsError()
    assert result["data"]["createCategory"]["message"] == err.message


@pytest.mark.asyncio
async def test_create_category_with_too_long_name_should_produce_error(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    name = "a" * 33
    mutation = f"""
        mutation newCategory {{
            createCategory(input: {{name: "{name}"}}) {{
                __typename
                ... on CategoryType {{
                    name
                }}
                ... on CategoryExistsError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "String should have at most 32 characters"
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_with_too_short_name_should_produce_error(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    name = ""
    mutation = f"""
        mutation newCategory {{
            createCategory(input: {{name: "{name}"}}) {{
                __typename
                ... on CategoryType {{
                    name
                }}
                ... on CategoryExistsError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "String should have at least 1 character"
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_capitalize_name(
    admin_client: httpx.AsyncClient, _db_session: AsyncSession
) -> None:
    name = "test"
    mutation = f"""
        mutation newCategory {{
            createCategory(input: {{name: "{name}"}}) {{
                __typename
                ... on CategoryType {{
                    name
                }}
                ... on CategoryExistsError {{
                    message
                }}
                ... on InputValidationError {{
                    message
                }}
            }}
        }}
    """
    response = await admin_client.post("/graphql", json={"query": mutation})
    result = response.json()
    query = select(Category)
    category_db = (await _db_session.execute(query)).scalar()
    assert result["data"]["createCategory"]["__typename"] == "CategoryType"
    assert result["data"]["createCategory"]["name"] == name.title()
    assert category_db
    assert category_db.name == name.title()


@pytest.mark.asyncio
@pytest.mark.parametrize("url", ["test", "test.com"])
async def test_adhoc_scan_invalid_input(client: httpx.AsyncClient, url: str) -> None:
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{url: "{url}"}}) {{
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
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "InputValidationError"
    assert "url" in result["data"]["adhocScan"]["message"]


@pytest.mark.asyncio
async def test_adhoc_scan_correct_response(
    client: httpx.AsyncClient, _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    category = Category(name="Plot")
    _db_session.add(category)
    await _db_session.commit()
    url = "https://www.test.io/test"
    schedule = {"day_of_week": 0, "hour": 1, "minute": 2}
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    schedule_mock = mocker.patch("api.parsing.setup_scan_periodic_task")
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{
                    url: "{url}",
                    schedule: {{hour: 1, dayOfWeek: 0, minute: 2}}
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
    response = await client.post("/graphql", json={"query": mutation})
    estates_parsed = (
        await _db_session.exec(select(Estate).options(selectinload(Estate.prices)))
    ).all()  # type: ignore
    prices_parsed = (await _db_session.exec(select(Price))).all()  # type: ignore
    search_parsed: Search = (
        await _db_session.exec(select(Search))  # type: ignore
    ).first()
    schedule_mock.assert_called_once()
    assert len(estates_parsed) == 36
    assert len(prices_parsed) == 36
    assert search_parsed.schedule == schedule
    assert estates_parsed[0].prices[0] in prices_parsed
    assert decode_url(search_parsed.url) == url  # type: ignore
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "ScanSucceeded"
    assert "Scan has finished" in result["data"]["adhocScan"]["message"]


@pytest.mark.asyncio
async def test_adhoc_scan_incorrect_category(
    client: httpx.AsyncClient, mocker: MockerFixture
) -> None:
    url = "https://www.test.io/test"
    with open("tests/example_files/body_plot.json", "r") as f:
        body = json.load(f)
    resp = MockAioJSONResponse(body, 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{url: "{url}"}}) {{
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
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "ScanFailedError"
    assert "Document parsing failed." in result["data"]["adhocScan"]["message"]


@pytest.mark.asyncio
async def test_adhoc_scan_404_response(
    client: httpx.AsyncClient, mocker: MockerFixture, cache: fakeredis.FakeRedis
) -> None:
    url = "https://www.test.io/test"
    with open("tests/example_files/404_resp.html", "r") as f:
        body = f.read()
    resp = MockAioTextResponse(body, 404)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)
    mocker.patch("asyncio.sleep", return_value=0)
    mutation = f"""
        mutation adhocScan {{
            adhocScan(input: {{url: "{url}"}}) {{
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
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["adhocScan"]["__typename"] == "ScanFailedError"
    assert (
        "Scan has failed with 404 status code."
        in result["data"]["adhocScan"]["message"]
    )
    assert cache.get("token") == "U-X80D14b5VUVY_qgIbBQ"


@pytest.mark.asyncio
async def test_search_event_stats_without_top(
    client: httpx.AsyncClient, _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    """
    SETUP
    """
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
            }}
        }}
    """
    await client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()
    query = f"""
        query eventStats {{
            searchEventStats(input: {{
                    id: {search_event.id}
                }}) {{
                __typename
                ... on EventStatsType {{
                avgAreaInSquareMeters
                avgTerrainAreaInSquareMeters
                avgPrice
                avgPricePerSquareMeter
                minPrice {{
                    price
                    areaInSquareMeters
                    estate {{
                    title
                    }}
                }}
                minPricePerSquareMeter {{
                    areaInSquareMeters
                    price
                    pricePerSquareMeter
                    estate {{
                    title
                    }}
                }}
                }}
                ... on SearchEventDoesntExistError {{
                    message
                }}
                ... on NoPricesFoundError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchEventStats"]
    expected_result = {
        "__typename": "EventStatsType",
        "avgAreaInSquareMeters": 1075.25,
        "avgPrice": 132315.72,
        "avgPricePerSquareMeter": 158.67,
        "avgTerrainAreaInSquareMeters": None,
        "minPrice": {
            "areaInSquareMeters": 1242,
            "estate": {"title": '"Działki na Żuławach"'},
            "price": 100000,
        },
        "minPricePerSquareMeter": {
            "areaInSquareMeters": 4900,
            "estate": {"title": "Z warunkami zabudowy nad " "Wisłą, piękna sceneria!"},
            "price": 129000,
            "pricePerSquareMeter": 26,
        },
    }
    assert result == expected_result


@pytest.mark.asyncio
async def test_search_event_doesnt_exist(
    client: httpx.AsyncClient, _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    """
    SETUP
    """
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
            }}
        }}
    """
    await client.post("/graphql", json={"query": mutation})
    search_event = (await _db_session.exec(select(SearchEvent))).first()
    query = f"""
        query eventStats {{
            searchEventStats(input: {{
                    id: {search_event.id + 1}
                }}) {{
                __typename
                ... on EventStatsType {{
                    avgPrice
                }}
                ... on SearchEventDoesntExistError {{
                    message
                }}
                ... on NoPricesFoundError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchEventStats"]
    assert result["__typename"] == "SearchEventDoesntExistError"
    assert result["message"] == "Search Event with provided id doesn't exist"


@pytest.mark.asyncio
async def test_search_doesnt_exist(
    client: httpx.AsyncClient, _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    """
    SETUP
    """
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
            }}
        }}
    """
    await client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    query = f"""
        query searchStats {{
            searchStats(input: {{
                    id: {search.id + 1}
                }}) {{
                __typename
                ... on SearchStatsType {{
                    avgPriceTotal
                }}
                ... on SearchDoesntExistError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchStats"]
    assert result["__typename"] == "SearchDoesntExistError"
    assert result["message"] == "Search with provided id doesn't exist"


@pytest.mark.asyncio
async def test_search_stats_query(
    client: httpx.AsyncClient, _db_session: AsyncSession, mocker: MockerFixture
) -> None:
    """
    SETUP
    """
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
            }}
        }}
    """
    await client.post("/graphql", json={"query": mutation})
    await client.post("/graphql", json={"query": mutation})
    search = (await _db_session.exec(select(Search))).first()
    query = f"""
        query searchStats {{
            searchStats(input: {{
                    id: {search.id}
                }}) {{
                __typename
                ... on SearchStatsType {{
                    avgAreaTotal
                    avgTerrainTotal
                    avgPricePerSquareMeterTotal
                    avgPriceTotal
                    category {{
                        name
                    }}
                    dateFrom
                    dateTo
                    distanceRadius
                    events {{
                        avgAreaInSquareMeters
                        avgPrice
                        avgPricePerSquareMeter
                        avgTerrainAreaInSquareMeters
                    }}
                    location
                    fromPrice
                    toPrice
                }}
                ... on SearchDoesntExistError {{
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": query})
    result = response.json()["data"]["searchStats"]
    expected = {
        "__typename": "SearchStatsType",
        "avgAreaTotal": 1075.25,
        "avgPricePerSquareMeterTotal": 158.67,
        "avgPriceTotal": 132315.72,
        "avgTerrainTotal": None,
        "category": {"name": "Plot"},
        "distanceRadius": 15,
        "events": [
            {
                "avgAreaInSquareMeters": 1075.25,
                "avgPrice": 132315.72,
                "avgPricePerSquareMeter": 158.67,
                "avgTerrainAreaInSquareMeters": None,
            },
            {
                "avgAreaInSquareMeters": 1075.25,
                "avgPrice": 132315.72,
                "avgPricePerSquareMeter": 158.67,
                "avgTerrainAreaInSquareMeters": None,
            },
        ],
        "fromPrice": 100000,
        "location": "Gdańsk, pomorskie",
        "toPrice": 150000,
    }
    result.pop("dateFrom")
    result.pop("dateTo")
    assert result == expected


@pytest.mark.asyncio
async def test_login_correct_credentials(
    client: httpx.AsyncClient, _db_session: AsyncSession, add_user: User
) -> None:
    """
    SETUP
    """
    email, password = examples["user"]["email"], examples["user"]["password"]
    mutation = f"""
        mutation login {{
            login(input: {{
                    email: "{email}", password: "{password}"
                }}) {{
                __typename
                ... on JWTPair {{
                    accessToken
                    refreshToken
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()["data"]["login"]
    assert result["__typename"] == "JWTPair"
    access_token, refresh_token = result["accessToken"], result["refreshToken"]
    access_token_decoded, refresh_token_decoded = get_jwt_payload(
        access_token
    ), get_jwt_payload(refresh_token)
    assert access_token_decoded["sub"] == str(add_user.id)
    assert refresh_token_decoded["sub"] == str(add_user.id)
    assert access_token_decoded["fresh"] is True
    assert refresh_token_decoded["fresh"] is False
    assert access_token_decoded["type"] == "access"
    assert refresh_token_decoded["type"] == "refresh"


@pytest.mark.asyncio
async def test_login_wrong_credentials(
    client: httpx.AsyncClient, _db_session: AsyncSession, add_user: User
) -> None:
    """
    SETUP
    """
    email, password = "invalid_email", examples["user"]["password"]
    mutation = f"""
        mutation login {{
            login(input: {{
                    email: "{email}", password: "{password}"
                }}) {{
                __typename
                ... on JWTPair {{
                    accessToken
                    refreshToken
                }}
                ... on LoginUserError {{
                    __typename
                    message
                }}
                ... on InputValidationError {{
                    __typename
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()["data"]["login"]
    assert result["__typename"] == "LoginUserError"
    assert result["message"] == "Login user error"

    email, password = examples["user"]["email"], "invalid_password"
    mutation = f"""
        mutation login {{
            login(input: {{
                    email: "{email}", password: "{password}"
                }}) {{
                __typename
                ... on JWTPair {{
                    accessToken
                    refreshToken
                }}
                ... on LoginUserError {{
                    __typename
                    message
                }}
                ... on InputValidationError {{
                    __typename
                    message
                }}
            }}
        }}
    """
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()["data"]["login"]
    assert result["__typename"] == "LoginUserError"
    assert result["message"] == "Login user error"
