from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth.dependencies import get_auth_service, get_current_user  # noqa: E402
from auth.routers.auth_router import router as auth_router  # noqa: E402
from auth.schemas import LoginRequest, RegisterRequest, RoleEnum, UserResponse  # noqa: E402
from auth.services.auth_service import AuthService  # noqa: E402


class FakeAuthService(AuthService):
    def __init__(self) -> None:
        self.users: dict[str, dict[str, object]] = {}
        self.refresh_tokens: set[str] = set()

    async def register_user(
        self, request: RegisterRequest, role: RoleEnum = RoleEnum.vendedor
    ) -> UserResponse:
        if request.email in self.users:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado",
            )
        now = datetime.now(UTC)
        user_id = f"user-{len(self.users) + 1}"
        user = UserResponse(
            id=user_id,
            email=request.email,
            full_name=request.full_name,
            role=role,
            is_active=True,
            created_at=now,
        )
        self.users[str(request.email)] = {
            "password": request.password,
            "user": user,
            "is_active": True,
        }
        return user

    async def authenticate_user(self, request: LoginRequest) -> tuple[str, str]:
        from fastapi import HTTPException, status

        record = self.users.get(str(request.email))
        if record is None or record["password"] != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
            )
        if not record["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada. Contacte al administrador",
            )
        user = record["user"]
        access_token = f"access-{user.id}"  # type: ignore[attr-defined]
        refresh_token = f"refresh-{user.id}"  # type: ignore[attr-defined]
        self.refresh_tokens.add(refresh_token)
        return access_token, refresh_token

    async def logout_user(self, refresh_token: str) -> None:
        from fastapi import HTTPException, status

        if refresh_token not in self.refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado"
            )
        self.refresh_tokens.remove(refresh_token)

    async def refresh_user_token(self, refresh_token: str) -> tuple[str, str]:
        from fastapi import HTTPException, status

        if refresh_token not in self.refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado"
            )
        self.refresh_tokens.remove(refresh_token)
        new_refresh_token = f"{refresh_token}-next"
        self.refresh_tokens.add(new_refresh_token)
        return "access-refreshed", new_refresh_token

    async def get_user_profile(self, user_id: str) -> UserResponse:
        for record in self.users.values():
            user = record["user"]
            if user.id == user_id:  # type: ignore[attr-defined]
                return user  # type: ignore[return-value]
        raise RuntimeError("user not found")


@pytest.fixture()
def fake_service(monkeypatch: pytest.MonkeyPatch) -> FakeAuthService:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    monkeypatch.setenv("JWT_REFRESH_COOKIE_SECURE", "false")

    service = FakeAuthService()
    now = datetime.now(UTC)
    service.users["admin@nexus.example.com"] = {
        "password": "Admin123",
        "is_active": True,
        "user": UserResponse(
            id="admin-1",
            email="admin@nexus.example.com",
            full_name="Admin Test",
            role=RoleEnum.admin,
            is_active=True,
            created_at=now,
        ),
    }
    service.users["seller@nexus.example.com"] = {
        "password": "Seller123",
        "is_active": True,
        "user": UserResponse(
            id="seller-1",
            email="seller@nexus.example.com",
            full_name="Seller Test",
            role=RoleEnum.vendedor,
            is_active=True,
            created_at=now,
        ),
    }
    service.users["inactive@nexus.example.com"] = {
        "password": "Inactive123",
        "is_active": False,
        "user": UserResponse(
            id="inactive-1",
            email="inactive@nexus.example.com",
            full_name="Inactive Test",
            role=RoleEnum.vendedor,
            is_active=False,
            created_at=now,
        ),
    }
    return service


def _build_app(service: FakeAuthService, current_user: UserResponse | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_auth_service] = lambda: service
    if current_user is not None:
        app.dependency_overrides[get_current_user] = lambda: current_user
    return app


@pytest.mark.asyncio
async def test_should_register_user_and_return_201_when_data_is_valid(
    fake_service: FakeAuthService,
) -> None:
    app = _build_app(
        fake_service,
        UserResponse(
            id="admin-1",
            email="admin@nexus.example.com",
            full_name="Admin Test",
            role=RoleEnum.admin,
            is_active=True,
            created_at=datetime.now(UTC),
        ),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "nuevo@nexus.example.com",
                "password": "Nueva123",
                "full_name": "Nuevo Usuario",
            },
        )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_should_return_409_when_email_already_exists(fake_service: FakeAuthService) -> None:
    app = _build_app(
        fake_service,
        UserResponse(
            id="admin-1",
            email="admin@nexus.example.com",
            full_name="Admin Test",
            role=RoleEnum.admin,
            is_active=True,
            created_at=datetime.now(UTC),
        ),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "seller@nexus.example.com",
                "password": "Nueva123",
                "full_name": "Nuevo Usuario",
            },
        )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_should_return_422_when_password_is_too_weak(fake_service: FakeAuthService) -> None:
    app = _build_app(
        fake_service,
        UserResponse(
            id="admin-1",
            email="admin@nexus.example.com",
            full_name="Admin Test",
            role=RoleEnum.admin,
            is_active=True,
            created_at=datetime.now(UTC),
        ),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={"email": "weak@nexus.example.com", "password": "weak", "full_name": "Weak User"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_should_login_and_return_access_token_when_credentials_are_valid(
    fake_service: FakeAuthService,
) -> None:
    app = _build_app(fake_service)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "seller@nexus.example.com", "password": "Seller123"},
        )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_should_return_401_when_credentials_are_invalid(
    fake_service: FakeAuthService,
) -> None:
    app = _build_app(fake_service)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "seller@nexus.example.com", "password": "Wrong123"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


@pytest.mark.asyncio
async def test_should_return_403_when_account_is_inactive(fake_service: FakeAuthService) -> None:
    app = _build_app(fake_service)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "inactive@nexus.example.com", "password": "Inactive123"},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_should_logout_and_invalidate_refresh_token(fake_service: FakeAuthService) -> None:
    app = _build_app(fake_service)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/auth/login", json={"email": "seller@nexus.example.com", "password": "Seller123"}
        )
        token = next(iter(fake_service.refresh_tokens))
        response = await client.post("/auth/logout", cookies={"refresh_token": token})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_should_refresh_token_and_rotate_pair_when_refresh_token_is_valid(
    fake_service: FakeAuthService,
) -> None:
    app = _build_app(fake_service)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/auth/login", json={"email": "seller@nexus.example.com", "password": "Seller123"}
        )
        token = next(iter(fake_service.refresh_tokens))
        response = await client.post("/auth/refresh", cookies={"refresh_token": token})

    assert response.status_code == 200
    assert response.json()["access_token"] == "access-refreshed"


@pytest.mark.asyncio
async def test_should_return_401_when_refresh_token_is_already_invalidated(
    fake_service: FakeAuthService,
) -> None:
    app = _build_app(fake_service)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/auth/refresh", cookies={"refresh_token": "invalid"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_should_return_403_when_role_is_insufficient(fake_service: FakeAuthService) -> None:
    app = _build_app(
        fake_service,
        UserResponse(
            id="seller-1",
            email="seller@nexus.example.com",
            full_name="Seller Test",
            role=RoleEnum.vendedor,
            is_active=True,
            created_at=datetime.now(UTC),
        ),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "nuevo2@nexus.example.com",
                "password": "Nueva123",
                "full_name": "Nuevo Usuario",
            },
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_should_return_me_with_user_data_when_token_is_valid(
    fake_service: FakeAuthService,
) -> None:
    user = UserResponse(
        id="seller-1",
        email="seller@nexus.example.com",
        full_name="Seller Test",
        role=RoleEnum.vendedor,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    app = _build_app(fake_service, user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "seller@nexus.example.com"

