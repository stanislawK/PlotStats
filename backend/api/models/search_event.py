from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from . import Estate, Price, Search


class SearchEventEstate(SQLModel, table=True):
    search_event_id: Optional[int] = Field(
        default=None, foreign_key="searchevent.id", primary_key=True
    )
    estate_id: Optional[int] = Field(
        default=None, foreign_key="estate.id", primary_key=True
    )

class SearchEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    estates: List["Estate"] = Relationship(back_populates="search_events", link_model=SearchEventEstate)
    search_id: Optional[int] = Field(default=None, foreign_key="search.id")
    search: Optional["Search"] = Relationship(back_populates="search_events")
    prices: List["Price"] = Relationship(back_populates="search_event")
