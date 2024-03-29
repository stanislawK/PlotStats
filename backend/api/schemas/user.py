from typing import Any

import strawberry
from loguru import logger
from passlib import pwd
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
from strawberry.types import Info

from api.models.user import User
from api.permissions import HasValidRefreshToken, IsAdminUser, IsFreshToken
from api.types.auth import (
    AccessToken,
    ActivateAccountError,
    ActivateAccountInput,
    ActivateAccountResponse,
    ActivateAccountSuccess,
    DeactivateAccountError,
    DeactivateAccountSuccess,
    DeactivateUserInput,
    DeactivateUserResponse,
    JWTPair,
    LoginUserData,
    LoginUserError,
    LoginUserResponse,
    NewUserInput,
    RefreshTokenError,
    RefreshTokenResponse,
    RegisterResponse,
    RegisterUserResponse,
    UserExistsError,
    UsersList,
    convert_users_from_db,
)
from api.types.general import InputValidationError
from api.utils.jwt import create_jwt_token
from api.utils.user import (
    authenticate_user,
    get_all_users,
    get_password_hash,
    get_user_by_email,
)


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAdminUser])  # type: ignore
    async def all_users(self, info: Info[Any, Any]) -> UsersList:
        session = info.context["session"]
        users_db = await get_all_users(session=session)
        return convert_users_from_db(users_db)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(
        self, info: Info[Any, Any], input: LoginUserData
    ) -> LoginUserResponse:
        # This will run pydantic's validation
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        session: AsyncSession = info.context["session"]
        user = await authenticate_user(session, data.email, data.password)
        if (
            not isinstance(user, User)
            or not user.is_active
            or "deactivated" in user.roles
        ):
            logger.error(f"{data.email} logging failed attempt")
            return LoginUserError()
        access_token = create_jwt_token(
            subject=str(user.id), fresh=True, token_type="access", roles=user.roles
        )
        refresh_token = create_jwt_token(
            subject=str(user.id), fresh=False, token_type="refresh", roles=user.roles
        )
        return JWTPair(access_token=access_token, refresh_token=refresh_token)

    @strawberry.mutation(permission_classes=[HasValidRefreshToken])  # type: ignore
    async def refresh_token(self, info: Info[Any, Any]) -> RefreshTokenResponse:
        user = getattr(info.context["request"].state, "user", None)
        if not isinstance(user, User):
            logger.error("Refresh token failed attempt")
            return RefreshTokenError()
        access_token = create_jwt_token(
            subject=str(user.id), fresh=False, token_type="access", roles=user.roles
        )
        return AccessToken(access_token=access_token)

    @strawberry.mutation(permission_classes=[IsAdminUser, IsFreshToken])  # type: ignore
    async def register_user(
        self, info: Info[Any, Any], input: NewUserInput
    ) -> RegisterUserResponse:
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        email = data.email
        session = info.context["session"]
        if await get_user_by_email(session, email):
            return UserExistsError()
        temporary_password = pwd.genword(entropy=68, charset="ascii_72")
        new_user = User(
            email=email,
            password=get_password_hash(temporary_password),
            is_active=False,
        )
        session.add(new_user)
        await session.commit()
        return RegisterResponse(temporary_password=temporary_password)

    @strawberry.mutation(permission_classes=[IsAdminUser, IsFreshToken])  # type: ignore
    async def deactivate_user(
        self, info: Info[Any, Any], input: DeactivateUserInput
    ) -> DeactivateUserResponse:
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        email = data.email
        session = info.context["session"]
        user = await get_user_by_email(session, email)
        if not user:
            return DeactivateAccountError()
        user.roles = ["deactivated"]
        user.is_active = False
        session.add(user)
        await session.commit()
        return DeactivateAccountSuccess()

    @strawberry.mutation
    async def activate_account(
        self, info: Info[Any, Any], input: ActivateAccountInput
    ) -> ActivateAccountResponse:
        # This will run pydantic's validation
        try:
            data = input.to_pydantic()
        except ValidationError as error:
            return InputValidationError(message=str(error))
        session: AsyncSession = info.context["session"]
        user = await authenticate_user(session, data.email, data.temp_password)
        if not isinstance(user, User):
            logger.error(f"{data.email} activate account failed attempt")
            return ActivateAccountError()
        if user.is_active or "user" not in user.roles or "deactivated" in user.roles:
            return ActivateAccountError()
        user.password = get_password_hash(data.new_password)
        user.is_active = True
        session.add(user)
        await session.commit()
        return ActivateAccountSuccess()
