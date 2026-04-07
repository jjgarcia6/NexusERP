from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from customers.utils.identification import validate_identification


class CustomerTypeEnum(str, Enum):
    persona_natural = "persona_natural"
    juridica = "juridica"


class CustomerRequest(BaseModel):
    # Keep enum parsing compatible with JSON string payloads.
    model_config = ConfigDict(strict=False)

    name: str = Field(
        min_length=2,
        max_length=150,
        description="Nombre completo o razon social. PII bajo LOPDP.",
    )
    customer_type: CustomerTypeEnum = Field(
        description="Tipo de cliente. Determina el formato de identificacion valido.",
    )
    identification_number: str = Field(
        description="Cedula (10 digitos) o RUC (13 digitos).",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Email de contacto. PII bajo LOPDP.",
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        description="Telefono de contacto. PII bajo LOPDP.",
    )
    address: str | None = Field(
        default=None,
        max_length=300,
        description="Direccion del cliente.",
    )

    @model_validator(mode="after")
    def validate_identification_format(self) -> CustomerRequest:
        if not validate_identification(self.identification_number, self.customer_type):
            raise ValueError(
                "Numero de identificacion invalido para el tipo de cliente seleccionado.",
            )
        return self


class CustomerResponse(BaseModel):
    model_config = ConfigDict(strict=False)

    id: str = Field(description="Identificador unico del cliente.")
    name: str = Field(description="Nombre completo o razon social.")
    customer_type: CustomerTypeEnum = Field(description="Tipo de cliente.")
    identification_number: str = Field(description="Cedula o RUC del cliente.")
    email: EmailStr | None = Field(description="Email de contacto.")
    phone: str | None = Field(description="Telefono de contacto.")
    address: str | None = Field(description="Direccion del cliente.")
    is_active: bool = Field(description="Estado del cliente. false equivale a soft delete.")
    created_at: datetime = Field(description="Fecha de creacion en UTC.")
    updated_at: datetime = Field(description="Fecha de ultima modificacion en UTC.")


class CustomerUpdateRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    # No incluye identification_number ni customer_type (campos inmutables)
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Nuevo nombre o razon social.",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Nuevo email de contacto.",
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        description="Nuevo telefono de contacto.",
    )
    address: str | None = Field(
        default=None,
        max_length=300,
        description="Nueva direccion.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Nuevo estado del cliente.",
    )


class CustomerSearchResult(BaseModel):
    model_config = ConfigDict(strict=False)

    id: str = Field(description="ID del cliente para el selector del POS.")
    name: str = Field(description="Nombre mostrado en el dropdown.")
    identification_number: str = Field(description="Identificacion mostrada en el selector.")
    customer_type: CustomerTypeEnum = Field(description="Tipo para representar el cliente en UI.")


class CustomerListResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[CustomerResponse] = Field(
        description="Lista de clientes de la pagina actual.",
    )
    total: int = Field(
        ge=0,
        description="Total de clientes activos que coinciden con los filtros.",
    )
    skip: int = Field(
        ge=0,
        description="Numero de documentos omitidos para paginacion.",
    )
    limit: int = Field(
        gt=0,
        description="Numero maximo de documentos retornados por pagina.",
    )
