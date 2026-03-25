from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from auth.dependencies import get_current_user, require_role
from auth.schemas import MessageResponse, RoleEnum, UserResponse
from catalog.dependencies import get_category_service
from catalog.schemas import CategoryRequest, CategoryResponse, CategoryUpdateRequest
from catalog.services.category_service import CategoryService

router = APIRouter()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryRequest,
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> CategoryResponse:
    return await service.create_category(payload)


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[UserResponse, Depends(get_current_user)],
) -> list[CategoryResponse]:
    return await service.list_categories()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[UserResponse, Depends(get_current_user)],
) -> CategoryResponse:
    return await service.get_category(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    payload: CategoryUpdateRequest,
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> CategoryResponse:
    return await service.update_category(category_id, payload)


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: str,
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> MessageResponse:
    await service.delete_category(category_id)
    return MessageResponse()
