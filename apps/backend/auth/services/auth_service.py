from __future__ import annotations

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from auth.repositories.token_repository import TokenRepository
from auth.repositories.user_repository import UserRepository
from auth.schemas import LoginRequest, RegisterRequest, RoleEnum, UserResponse
from auth.utils.jwt import create_access_token, create_refresh_token, decode_token
from auth.utils.password import hash_password, verify_password
from core.settings import get_settings


class AuthService:
    def __init__(self, user_repository: UserRepository, token_repository: TokenRepository) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.settings = get_settings()

    async def register_user(
        self,
        request: RegisterRequest,
        role: RoleEnum = RoleEnum.vendedor,
    ) -> UserResponse:
        hashed = hash_password(request.password)
        try:
            user = await self.user_repository.create_user(
                email=request.email,
                hashed_password=hashed,
                full_name=request.full_name,
                role=role,
            )
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado",
            ) from exc

        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user["full_name"],
            role=RoleEnum(user["role"]),
            is_active=bool(user["is_active"]),
            created_at=user["created_at"],
        )

    async def authenticate_user(self, request: LoginRequest) -> tuple[str, str]:
        user = await self.user_repository.find_by_email(str(request.email))
        if user is None or not verify_password(request.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        if not bool(user["is_active"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada. Contacte al administrador",
            )

        user_id = str(user["_id"])
        role = str(user["role"])
        access_token = create_access_token({"sub": user_id, "role": role})
        refresh_token = create_refresh_token({"sub": user_id, "role": role})
        await self.token_repository.save_token(
            token=refresh_token,
            user_id=user_id,
            expires_in_days=self.settings.jwt_refresh_token_expire_days,
        )

        return access_token, refresh_token

    async def logout_user(self, refresh_token: str) -> None:
        deleted = await self.token_repository.delete_token(refresh_token)
        if deleted == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
            )

    async def refresh_user_token(self, refresh_token: str) -> tuple[str, str]:
        decoded = decode_token(refresh_token)
        saved = await self.token_repository.find_token(refresh_token)
        if saved is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
            )

        await self.token_repository.delete_token(refresh_token)
        access_token = create_access_token({"sub": decoded["sub"], "role": decoded["role"]})
        new_refresh_token = create_refresh_token({"sub": decoded["sub"], "role": decoded["role"]})
        await self.token_repository.save_token(
            token=new_refresh_token,
            user_id=str(decoded["sub"]),
            expires_in_days=self.settings.jwt_refresh_token_expire_days,
        )

        return access_token, new_refresh_token

    async def get_user_profile(self, user_id: str) -> UserResponse:
        user = await self.user_repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
            )

        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user["full_name"],
            role=RoleEnum(user["role"]),
            is_active=bool(user["is_active"]),
            created_at=user["created_at"],
        )
