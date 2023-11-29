from typing import Optional

from models.user import User
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> Optional[User]:
    user: Optional[User] = (
        await session.exec(select(User).where(User.email == email))  # type: ignore
    ).first()
    return user


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
    user = get_user_by_email(session, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
