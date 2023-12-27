from typing import Any

from fastapi import Request
from strawberry.permission import BasePermission
from strawberry.types import Info

from api.utils.jwt import (
    PermissionDeniedError,
    extract_token_from_request,
    get_jwt_payload,
    get_user_from_token,
)


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(  # type: ignore
        self, source: Any, info: Info, **kwargs  # type: ignore
    ) -> bool:
        request: Request = info.context["request"]
        token = extract_token_from_request(request)
        if not token:
            return False
        try:
            user = await get_user_from_token(token, info.context["session"])
        except PermissionDeniedError:
            return False
        if user:
            request.state.user = user
            return True
        return False


class IsAdminUser(BasePermission):
    message = "User is not authenticated"

    async def has_permission(  # type: ignore
        self, source: Any, info: Info, **kwargs  # type: ignore
    ) -> bool:
        request: Request = info.context["request"]
        token = extract_token_from_request(request)
        if not token:
            return False
        try:
            user = await get_user_from_token(token, info.context["session"])
        except PermissionDeniedError:
            return False
        if user and isinstance(user.roles, list) and "admin" in user.roles:
            request.state.user = user
            return True
        return False


class HasValidRefreshToken(BasePermission):
    message = "User is not authenticated"

    async def has_permission(  # type: ignore
        self, source: Any, info: Info, **kwargs  # type: ignore
    ) -> bool:
        request: Request = info.context["request"]
        token = extract_token_from_request(request)
        if not token:
            return False
        try:
            user = await get_user_from_token(
                token, info.context["session"], refresh=True
            )
        except PermissionDeniedError:
            return False
        if user:
            request.state.user = user
            return True
        return False


class IsFreshToken(BasePermission):
    message = "Please login again"

    def has_permission(
        self, source: Any, info: Info, **kwargs: Any  # type: ignore
    ) -> bool:
        request: Request = info.context["request"]
        token = extract_token_from_request(request)
        if not token:
            return False
        decoded_token = get_jwt_payload(token)
        if not isinstance(is_fresh := decoded_token.get("fresh"), bool):
            return False
        else:
            return is_fresh
