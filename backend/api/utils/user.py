from typing import Optional

from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> Optional[User]:
    user: Optional[User] = (
        await session.exec(select(User).where(User.email == email))
    ).first()
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)  # type: ignore


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> User | bool:
    user = await get_user_by_email(session, email)
    if not user or not password:
        return False
    if not verify_password(password, user.password):
        return False
    return user
