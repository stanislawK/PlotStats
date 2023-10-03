import pytest
from pydantic.error_wrappers import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models import Category, Estate, Price, Search, SearchEvent, User
from api.models.search import decode_url, encode_url

from .conftest import examples


@pytest.mark.asyncio
async def test_category(_db_session: AsyncSession) -> None:
    category = Category(**examples["category"])
    _db_session.add(category)
    await _db_session.commit()
    from_db = (await _db_session.execute(select(Category))).scalar()
    for key, value in examples["category"].items():
        assert getattr(from_db, key) == value


@pytest.mark.asyncio
async def test_search(_db_session: AsyncSession) -> None:
    category = Category(**examples["category"])
    search_data = examples["search"].copy()
    org_url = search_data.pop("url")
    search = Search(
        url=encode_url(org_url), **search_data, category=category  # type:ignore
    )
    _db_session.add(search)
    await _db_session.commit()
    from_db: Search | None = (await _db_session.execute(select(Search))).scalar()
    assert from_db is not None
    for key, value in search_data.items():
        assert getattr(from_db, key) == value
    assert decode_url(from_db.url) == org_url  # type:ignore
    assert from_db.category is not None
    assert from_db.category.name == category.name


@pytest.mark.asyncio
async def test_user(_db_session: AsyncSession) -> None:
    search = Search(**examples["search"])
    user = User(**examples["user"], searches=[search])
    _db_session.add(user)
    await _db_session.commit()
    from_db: User | None = (await _db_session.execute(select(User))).scalar()
    assert from_db is not None
    for key, value in examples["user"].items():
        assert getattr(from_db, key) == value
    assert from_db.searches[0] == search

    # Not unique email should fail
    # Invalid email should fail
    for email in ("john@test.com", "test"):
        with pytest.raises((IntegrityError, ValidationError)) as exc_info:
            User.validate({"email": email})
            user = User(email=email)
            _db_session.add(user)
            await _db_session.commit()
        exc_type = type(exc_info.value)
        if exc_type == IntegrityError:
            assert "UNIQUE constraint failed" in str(exc_info.value)
        elif exc_type == ValidationError:
            assert "value is not a valid email address" in str(exc_info.value)
        else:
            assert False, f"Unexpected exception type {exc_type}"


@pytest.mark.asyncio
async def test_search_event(_db_session: AsyncSession) -> None:
    estate = Estate(**examples["estate"])
    search = Search(**examples["search"])
    price = Price(**examples["price"], estate=estate)
    search_event = SearchEvent(estates=[estate], search=search, prices=[price])
    _db_session.add(search_event)
    await _db_session.commit()
    from_db: SearchEvent | None = (
        await _db_session.execute(select(SearchEvent))
    ).scalar()
    assert from_db is not None
    assert from_db.search == search
    assert from_db.prices[0] == price
    assert from_db.estates[0] == estate
