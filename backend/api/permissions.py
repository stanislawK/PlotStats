from typing import Any

from fastapi import Request
from strawberry.permission import BasePermission
from strawberry.types import Info

from api.utils.jwt import (
    PermissionDeniedError,
    extract_token_from_request,
    get_user_from_token,
)


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:  # type: ignore
        request: Request = info.context["request"]
        token = extract_token_from_request(request)
        if not token:
            return False
        try:
            user = get_user_from_token(token, info.context["session"])
        except PermissionDeniedError:
            return False
        if user:
            request.state.user = user
            return True
        return False
