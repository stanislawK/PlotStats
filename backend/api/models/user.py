from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .search import Search


class SearchUser(SQLModel, table=True):
    search_id: Optional[int] = Field(
        default=None, foreign_key="search.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    searches: List["Search"] = Relationship(
        back_populates="users", link_model=SearchUser
    )
