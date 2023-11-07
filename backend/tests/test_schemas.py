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
from api.types.category import CategoryExistsError

from .conftest import MockAioJSONResponse, MockAioTextResponse, examples


@pytest.mark.asyncio
async def test_categories_query(
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
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]["categories"]) == 1
    assert result["data"]["categories"][0]["name"] == examples["category"]["name"]


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
    client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryType"
    assert result["data"]["createCategory"]["name"] == "Test2"
    query = select(Category).where(Category.name == "Test2")
    category_db = (await _db_session.execute(query)).scalar()
    assert category_db.name == "Test2"  # type: ignore


@pytest.mark.asyncio
async def test_create_category_mutation_duplicate_should_produce_error(
    client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "CategoryExistsError"
    err = CategoryExistsError()
    assert result["data"]["createCategory"]["message"] == err.message


@pytest.mark.asyncio
async def test_create_category_with_too_long_name_should_produce_error(
    client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "ensure this value has at most 32 characters"
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_with_too_short_name_should_produce_error(
    client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await client.post("/graphql", json={"query": mutation})
    result = response.json()
    assert result["data"]["createCategory"]["__typename"] == "InputValidationError"
    assert (
        "ensure this value has at least 1 characters "
        in result["data"]["createCategory"]["message"]
    )


@pytest.mark.asyncio
async def test_create_category_capitalize_name(
    client: httpx.AsyncClient, _db_session: AsyncSession
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
    response = await client.post("/graphql", json={"query": mutation})
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
