from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator


class CategoryBase(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(
        min_length=2,
        max_length=80,
        description="Nombre descriptivo de la categoria.",
    )
    description: str | None = Field(
        default=None,
        max_length=300,
        description="Descripcion opcional de la categoria.",
    )


class CategoryRequest(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(strict=True)

    id: str = Field(description="Identificador unico serializado desde ObjectId.")
    is_active: bool = Field(description="Estado de la categoria.")
    created_at: datetime = Field(description="Fecha de creacion en UTC.")
    updated_at: datetime = Field(description="Fecha de ultima modificacion en UTC.")


class CategoryUpdateRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=80,
        description="Nuevo nombre de la categoria. Opcional en actualizacion parcial.",
    )
    description: str | None = Field(
        default=None,
        max_length=300,
        description="Nueva descripcion. Opcional en actualizacion parcial.",
    )


class ProductBase(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(
        min_length=2,
        max_length=150,
        description="Nombre del producto. Usado en busqueda y en el POS.",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Descripcion detallada del producto.",
    )
    sku: str | None = Field(
        default=None,
        max_length=50,
        description="Codigo de referencia interno. Unico cuando se provee.",
    )
    price: Decimal = Field(
        gt=0,
        strict=False,
        decimal_places=2,
        description="Precio de venta al publico. Siempre positivo.",
    )
    cost: Decimal | None = Field(
        default=None,
        gt=0,
        strict=False,
        decimal_places=2,
        description="Precio de costo. Solo visible para admin.",
    )
    category_id: str = Field(
        description="ID de la categoria. DEBE existir en la coleccion categories.",
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL externa de imagen del producto.",
    )


class ProductRequest(ProductBase):
    pass


class ProductResponse(ProductBase):
    model_config = ConfigDict(strict=True)

    id: str = Field(description="Identificador unico serializado desde ObjectId.")
    category_name: str = Field(
        description="Nombre de la categoria calculado via lookup en MongoDB.",
    )
    is_active: bool = Field(description="Estado del producto. False indica soft delete.")
    created_at: datetime = Field(description="Fecha de creacion en UTC.")
    updated_at: datetime = Field(description="Fecha de ultima modificacion en UTC.")

    @model_validator(mode="before")
    @classmethod
    def hide_cost_for_non_admin(
        cls,
        data: dict[str, object],
        info: ValidationInfo,
    ) -> dict[str, object]:
        role = (info.context or {}).get("role")
        if role != "admin":
            data["cost"] = None
        return data


class ProductUpdateRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Nuevo nombre del producto.",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Nueva descripcion del producto.",
    )
    sku: str | None = Field(
        default=None,
        max_length=50,
        description="Nuevo SKU del producto.",
    )
    price: Decimal | None = Field(
        default=None,
        gt=0,
        strict=False,
        decimal_places=2,
        description="Nuevo precio de venta.",
    )
    cost: Decimal | None = Field(
        default=None,
        gt=0,
        strict=False,
        decimal_places=2,
        description="Nuevo precio de costo.",
    )
    category_id: str | None = Field(
        default=None,
        description="Nueva categoria del producto.",
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
        description="Nueva URL de imagen.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Nuevo estado. False indica soft delete.",
    )


class ProductListResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[ProductResponse] = Field(description="Lista de productos de la pagina actual.")
    total: int = Field(
        ge=0,
        description="Total de productos activos que coinciden con los filtros aplicados.",
    )
    skip: int = Field(ge=0, description="Numero de documentos omitidos para paginacion.")
    limit: int = Field(gt=0, description="Numero maximo de documentos retornados por pagina.")
