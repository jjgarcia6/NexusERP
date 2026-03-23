from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RoleEnum(str, Enum):
    admin = "admin"
    vendedor = "vendedor"
    bodeguero = "bodeguero"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr = Field(description="Correo electrónico para la nueva cuenta.")
    password: str = Field(
        min_length=8,
        description="Contraseña en texto plano. Se hashea antes de persistir. Nunca se loguea.",
    )
    full_name: str = Field(
        min_length=2,
        max_length=100,
        description="Nombre completo del usuario. Dato personal bajo LOPDP.",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(char.isdigit() for char in value):
            raise ValueError("La contraseña debe contener al menos un número")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr = Field(description="Correo electrónico del usuario.")
    password: str = Field(description="Contraseña en texto plano para verificación.")


class UserResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    id: str = Field(description="Identificador único del usuario serializado desde ObjectId.")
    email: EmailStr = Field(description="Correo electrónico del usuario.")
    full_name: str = Field(description="Nombre completo del usuario.")
    role: RoleEnum = Field(description="Rol del usuario. Determina permisos de acceso.")
    is_active: bool = Field(description="Estado de la cuenta. False = cuenta desactivada.")
    created_at: datetime = Field(description="Fecha de creación en UTC. ISO 8601.")


class TokenResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    access_token: str = Field(description="JWT de acceso. TTL 15 minutos.")
    token_type: Literal["bearer"] = Field(
        default="bearer",
        description="Tipo de token OAuth2. Siempre 'bearer'.",
    )


class MessageResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    message: Literal["ok"] = Field(default="ok", description="Resultado exitoso de la operación.")
