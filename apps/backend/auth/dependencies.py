from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.repositories.token_repository import TokenRepository
from auth.repositories.user_repository import UserRepository
from auth.schemas import RoleEnum, UserResponse
from auth.services.auth_service import AuthService
from auth.utils.jwt import decode_token
from core.database import get_database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service() -> AuthService:
    database = get_database()
    user_repository = UserRepository(database)
    token_repository = TokenRepository(database)
    return AuthService(user_repository, token_repository)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserResponse:
    decoded = decode_token(token)
    service = get_auth_service()
    user = await service.get_user_profile(str(decoded["sub"]))
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada. Contacte al administrador",
        )
    return user


def require_role(*roles: RoleEnum) -> Callable[..., Awaitable[UserResponse]]:
    async def _role_dependency(
        current_user: Annotated[UserResponse, Depends(get_current_user)],
    ) -> UserResponse:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes para esta operación",
            )
        return current_user

    return _role_dependency
