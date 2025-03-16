from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, Relationship, SQLModel

from .search_event import SearchEvent, SearchEventEstate

if TYPE_CHECKING:
    from . import Price


class Estate(SQLModel, table=True):
    id: int = Field(
        default=None,
        sa_column=Column(BigInteger(), primary_key=True, autoincrement=False),
    )
    title: str
    street: Optional[str] = Field(default=None)
    city: Optional[str] = Field(index=True)
    province: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    date_created: Optional[datetime] = Field(default=None)
    url: str
    search_events: List[SearchEvent] = Relationship(
        back_populates="estates", link_model=SearchEventEstate
    )
    prices: List["Price"] = Relationship(back_populates="estate")
