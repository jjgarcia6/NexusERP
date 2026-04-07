from __future__ import annotations

import random
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException, status
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth.dependencies import get_current_user
from auth.schemas import RoleEnum, UserResponse
from customers.dependencies import get_customer_service
from customers.routers.customers_router import router as customers_router
from customers.schemas import CustomerRequest, CustomerUpdateRequest


def _build_valid_cedula() -> str:
    coefficients = (2, 1, 2, 1, 2, 1, 2, 1, 2)
    province = f"{random.randint(1, 24):02d}"
    third_digit = str(random.randint(0, 5))
    body = province + third_digit + "654321"

    total = 0
    for index, coefficient in enumerate(coefficients):
        value = int(body[index]) * coefficient
        if value >= 10:
            value -= 9
        total += value

    verifier = 0 if total % 10 == 0 else 10 - (total % 10)
    return body + str(verifier)


def _build_valid_ruc_private() -> str:
    coefficients = (4, 3, 2, 7, 6, 5, 4, 3, 2)
    province = f"{random.randint(1, 24):02d}"
    third_digit = "9"
    while True:
        # Some sequences produce verifier=10, which is not a valid decimal digit.
        body = province + third_digit + f"{random.randint(0, 999999):06d}"
        total = sum(int(body[index]) * coefficient for index, coefficient in enumerate(coefficients))
        remainder = total % 11
        verifier = 0 if remainder == 0 else 11 - remainder
        if verifier == 11:
            verifier = 0
        if verifier < 10:
            return body + str(verifier) + "001"


class FakeCustomerService:
    def __init__(self) -> None:
        self.customers: dict[str, dict[str, object]] = {}

    async def create_customer(self, payload: CustomerRequest, *, created_by: str) -> dict[str, object]:
        if any(
            customer["identification_number"] == payload.identification_number
            for customer in self.customers.values()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un cliente con ese numero de identificacion",
            )

        customer_id = f"cus-{len(self.customers) + 1}"
        now = datetime.now(UTC)
        customer = {
            "id": customer_id,
            "name": payload.name,
            "customer_type": payload.customer_type.value,
            "identification_number": payload.identification_number,
            "email": payload.email,
            "phone": payload.phone,
            "address": payload.address,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "created_by": created_by,
        }
        self.customers[customer_id] = customer
        return customer

    async def list_customers(
        self,
        *,
        search: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, object]], int]:
        values = [customer for customer in self.customers.values() if bool(customer["is_active"])]
        if search:
            lowered = search.lower()
            values = [
                customer
                for customer in values
                if lowered in str(customer["name"]).lower()
                or lowered in str(customer["identification_number"]).lower()
            ]
        total = len(values)
        page = values[skip : skip + limit]
        return page, total

    async def search_customers(self, query: str, *, limit: int = 10) -> list[dict[str, object]]:
        lowered = query.lower()
        matches = [
            customer
            for customer in self.customers.values()
            if bool(customer["is_active"])
            and (
                lowered in str(customer["name"]).lower()
                or lowered in str(customer["identification_number"]).lower()
            )
        ][:limit]
        return [
            {
                "id": customer["id"],
                "name": customer["name"],
                "identification_number": customer["identification_number"],
                "customer_type": customer["customer_type"],
            }
            for customer in matches
        ]

    async def get_customer(self, customer_id: str) -> dict[str, object]:
        customer = self.customers.get(customer_id)
        if customer is None or not bool(customer["is_active"]):
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return customer

    async def update_customer(
        self,
        customer_id: str,
        payload: CustomerUpdateRequest,
        *,
        actor_role: RoleEnum,
    ) -> dict[str, object]:
        customer = self.customers.get(customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        updates = payload.model_dump(exclude_none=True)
        if updates.get("is_active") is False and actor_role != RoleEnum.admin:
            raise HTTPException(status_code=403, detail="Solo un administrador puede desactivar clientes")

        customer.update(updates)
        customer["updated_at"] = datetime.now(UTC)
        return customer


def _build_user(role: RoleEnum) -> UserResponse:
    return UserResponse(
        id=f"{role.value}-1",
        email=f"{role.value}@nexus.example.com",
        full_name=f"{role.value.title()} User",
        role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


def _build_app(service: FakeCustomerService, user: UserResponse) -> FastAPI:
    app = FastAPI()
    app.include_router(customers_router, prefix="/customers")
    app.dependency_overrides[get_customer_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: user
    return app


@pytest.mark.asyncio
async def test_should_create_persona_natural_customer_with_valid_cedula() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/customers",
            json={
                "name": "Cliente Uno",
                "customer_type": "persona_natural",
                "identification_number": _build_valid_cedula(),
                "email": "cliente1@nexus.example.com",
            },
        )

    assert response.status_code == 201
    assert response.json()["customer_type"] == "persona_natural"


@pytest.mark.asyncio
async def test_should_create_juridica_customer_with_valid_ruc() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/customers",
            json={
                "name": "Comercial ABC",
                "customer_type": "juridica",
                "identification_number": _build_valid_ruc_private(),
            },
        )

    assert response.status_code == 201
    assert response.json()["customer_type"] == "juridica"


@pytest.mark.asyncio
async def test_should_return_422_when_cedula_has_invalid_verifier_digit() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.admin))
    valid_cedula = _build_valid_cedula()
    invalid_cedula = valid_cedula[:-1] + str((int(valid_cedula[-1]) + 1) % 10)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/customers",
            json={
                "name": "Cliente Invalido",
                "customer_type": "persona_natural",
                "identification_number": invalid_cedula,
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_should_return_409_when_identification_number_already_exists() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.admin))
    cedula = _build_valid_cedula()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post(
            "/customers",
            json={
                "name": "Cliente Uno",
                "customer_type": "persona_natural",
                "identification_number": cedula,
            },
        )
        second = await client.post(
            "/customers",
            json={
                "name": "Cliente Duplicado",
                "customer_type": "persona_natural",
                "identification_number": cedula,
            },
        )

    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_should_update_customer_name_without_changing_identification() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.admin))
    cedula = _build_valid_cedula()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/customers",
            json={
                "name": "Cliente Uno",
                "customer_type": "persona_natural",
                "identification_number": cedula,
            },
        )
        customer_id = created.json()["id"]
        updated = await client.patch(
            f"/customers/{customer_id}",
            json={"name": "Cliente Actualizado"},
        )

    assert updated.status_code == 200
    assert updated.json()["name"] == "Cliente Actualizado"
    assert updated.json()["identification_number"] == cedula


@pytest.mark.asyncio
async def test_should_deactivate_customer_and_keep_document() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/customers",
            json={
                "name": "Cliente Uno",
                "customer_type": "persona_natural",
                "identification_number": _build_valid_cedula(),
            },
        )
        customer_id = created.json()["id"]
        deactivated = await client.patch(
            f"/customers/{customer_id}",
            json={"is_active": False},
        )
        listed = await client.get("/customers")

    assert deactivated.status_code == 200
    assert len(listed.json()["items"]) == 0
    assert customer_id in service.customers


@pytest.mark.asyncio
async def test_should_return_search_results_with_only_four_fields() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.vendedor))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/customers",
            json={
                "name": "Cliente Uno",
                "customer_type": "persona_natural",
                "identification_number": _build_valid_cedula(),
                "email": "cliente@nexus.example.com",
            },
        )
        response = await client.get("/customers/search", params={"q": "Cliente"})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert set(response.json()[0].keys()) == {
        "id",
        "name",
        "identification_number",
        "customer_type",
    }


@pytest.mark.asyncio
async def test_should_return_empty_list_when_search_has_no_results() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.vendedor))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/customers/search", params={"q": "NoExiste"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_should_return_400_when_search_query_has_less_than_two_chars() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.vendedor))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/customers/search", params={"q": "a"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_should_return_403_when_bodeguero_tries_to_access_customers_module() -> None:
    service = FakeCustomerService()
    app = _build_app(service, _build_user(RoleEnum.bodeguero))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/customers",
            json={
                "name": "Cliente Uno",
                "customer_type": "persona_natural",
                "identification_number": _build_valid_cedula(),
            },
        )

    assert response.status_code == 403
