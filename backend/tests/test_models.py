import pytest
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from pydantic.error_wrappers import ValidationError
from api.models import Category, Estate, Price, Search, SearchEvent, User
from .conftest import examples

def test_category(_db_session: Session):
    category = Category(**examples["category"])
    _db_session.add(category)
    _db_session.commit()
    from_db = _db_session.exec(select(Category)).first()
    for key, value in examples["category"].items():
        assert getattr(from_db, key) == value

def test_search(_db_session: Session):
    category = Category(**examples["category"])
    search = Search(**examples["search"], category=category)
    _db_session.add(search)
    _db_session.commit()
    from_db = _db_session.exec(select(Search)).first()
    for key, value in examples["search"].items():
        assert getattr(from_db, key) == value
    assert from_db.category.name == category.name

def test_user(_db_session: Session):
    search = Search(**examples["search"])
    user = User(**examples["user"], searches=[search])
    _db_session.add(user)
    _db_session.commit()
    from_db = _db_session.exec(select(User)).first()
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
            _db_session.commit()
        exc_type = type(exc_info.value)
        if exc_type == IntegrityError:
            assert "UNIQUE constraint failed" in str(exc_info.value)
        elif exc_type == ValidationError:
            assert "value is not a valid email address" in str(exc_info.value)
        else:
            assert False, f"Unexpected exception type {exc_type}"

def test_search_event(_db_session: Session):
    estate = Estate(**examples["estate"])
    search = Search(**examples["search"])
    price = Price(**examples["price"], estate=estate)
    search_event = SearchEvent(estates=[estate], search=search, prices=[price])
    _db_session.add(search_event)
    _db_session.commit()
    from_db = _db_session.exec(select(SearchEvent)).first()
    assert from_db.search == search
    assert from_db.prices[0] == price
    assert from_db.estates[0] == estate
