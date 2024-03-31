from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import Search


class ScanFailure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    search_id: int | None = Field(default=None, foreign_key="search.id")
    search: Optional["Search"] = Relationship(back_populates="failures")
    status_code: int = Field(index=True)
