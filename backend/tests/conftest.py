import os
import tempfile

import pytest
from sqlmodel import create_engine, SQLModel


@pytest.fixture
def _db():
    """Create temporary database for tests"""
    db_fd, db_path = tempfile.mkstemp()
    sqlite_url = f"sqlite://{db_path}"
    engine = create_engine(sqlite_url, echo=True)
    SQLModel.metadata.create_all(engine)
    os.close(db_fd)
    os.unlink(db_path)