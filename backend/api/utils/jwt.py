import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Request
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.user import User
from api.settings import settings

JWT_UNAUTHORIZED_MSG = "401_UNAUTHORIZED"
JWT_EXPIRED_MSG = "JWT_EXPIRED"
JWT_AUTH_HEADER_PREFIX = "Bearer "


class PermissionDeniedError(Exception):
    def __init__(self, message: str = JWT_UNAUTHORIZED_MSG):
        super().__init__(message)


def create_jwt_token(subject: str, fresh: bool, token_type: str = "access") -> str:
    now = datetime.now(timezone.utc)
    token_data = {
        "fresh": fresh,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": token_type,
        "sub": subject,
    }

    expires_delta = (
        timedelta(minutes=settings.access_token_expire_minutes)
        if token_type == "access"
        else timedelta(minutes=settings.refresh_token_expire_minutes)
    )
    expire = now + expires_delta
    token_data.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        token_data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_jwt_token(token: str) -> dict[str, Any]:
    return jwt.decode(  # type: ignore
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )


def get_jwt_payload(token: str) -> dict[str, Any]:
    try:
        decoded_token = decode_jwt_token(token)
    except JWTError:
        raise PermissionDeniedError()
    required_keys = ("exp", "iat", "jti", "type", "sub")
    if not all((key in decoded_token for key in required_keys)):
        raise PermissionDeniedError()
    if "fresh" not in decoded_token:
        decoded_token["fresh"] = False
    return decoded_token


def verify_token_type(type: str, refresh: bool) -> None:
    if (refresh and not type == "refresh") or (not refresh and not type == "access"):
        raise PermissionDeniedError()


async def get_user_from_payload(
    payload: dict[str, Any], session: AsyncSession, refresh: bool = False
) -> User:
    verify_token_type(payload["type"], refresh)
    id = payload["sub"]

    if not id:
        raise PermissionDeniedError()

    user: Optional[User] = (
        await session.exec(select(User).where(User.id == id))  # type: ignore
    ).first()
    if not user or not user.is_active:
        raise PermissionDeniedError()

    return user


async def get_user_from_token(token: str, session: AsyncSession) -> User:
    payload = get_jwt_payload(token)
    return await get_user_from_payload(payload, session)


def extract_token_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "").split()
    prefix = JWT_AUTH_HEADER_PREFIX

    if len(auth) != 2 or auth[0].lower() != prefix.lower():
        return None
    return auth[1]
