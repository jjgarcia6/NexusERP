from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from auth.dependencies import get_auth_service, get_current_user, require_role
from auth.schemas import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    RoleEnum,
    TokenResponse,
    UserResponse,
)
from auth.services.auth_service import AuthService
from core.settings import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=settings.jwt_refresh_cookie_secure,
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    return await service.register_user(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    access_token, refresh_token = await service.authenticate_user(payload)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> MessageResponse:
    if refresh_token is None:
        response.delete_cookie("refresh_token")
        return MessageResponse()

    await service.logout_user(refresh_token)
    response.delete_cookie("refresh_token")
    return MessageResponse()


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenResponse:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    access_token, next_refresh_token = await service.refresh_user_token(refresh_token)
    _set_refresh_cookie(response, next_refresh_token)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    return current_user
