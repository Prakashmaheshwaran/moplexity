from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import LLMProvider, LLMModel
from app.schemas import (
    LLMProviderCreate,
    LLMProviderUpdate,
    LLMProviderResponse,
    LLMModelCreate,
    LLMModelUpdate,
    LLMModelResponse,
    LLMModelActiveResponse
)

router = APIRouter()


# Provider endpoints
@router.get("/providers", response_model=List[LLMProviderResponse])
async def get_providers(db: AsyncSession = Depends(get_db)):
    """Get all LLM providers"""
    result = await db.execute(
        select(LLMProvider).options(joinedload(LLMProvider.models))
    )
    providers = result.scalars().all()
    return providers


@router.post("/providers", response_model=LLMProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(provider: LLMProviderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new LLM provider"""
    # Check if provider name already exists
    result = await db.execute(
        select(LLMProvider).where(LLMProvider.name == provider.name)
    )
    existing_provider = result.scalar_one_or_none()
    if existing_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider with this name already exists"
        )

    db_provider = LLMProvider(**provider.dict())
    db.add(db_provider)
    await db.commit()
    await db.refresh(db_provider)

    # Load models relationship
    result = await db.execute(
        select(LLMProvider).options(joinedload(LLMProvider.models)).where(LLMProvider.id == db_provider.id)
    )
    db_provider = result.scalar_one()

    return db_provider


@router.get("/providers/{provider_id}", response_model=LLMProviderResponse)
async def get_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific LLM provider"""
    result = await db.execute(
        select(LLMProvider).options(joinedload(LLMProvider.models)).where(LLMProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )
    return provider


@router.put("/providers/{provider_id}", response_model=LLMProviderResponse)
async def update_provider(
    provider_id: int,
    provider_update: LLMProviderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an LLM provider"""
    result = await db.execute(
        select(LLMProvider).where(LLMProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    # Check if new name conflicts with existing provider
    if provider_update.name:
        result = await db.execute(
            select(LLMProvider).where(LLMProvider.name == provider_update.name, LLMProvider.id != provider_id)
        )
        existing_provider = result.scalar_one_or_none()
        if existing_provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider with this name already exists"
            )

    # Update provider fields
    for field, value in provider_update.dict(exclude_unset=True).items():
        setattr(provider, field, value)

    await db.commit()
    await db.refresh(provider)

    # Load models relationship
    result = await db.execute(
        select(LLMProvider).options(joinedload(LLMProvider.models)).where(LLMProvider.id == provider_id)
    )
    provider = result.scalar_one()

    return provider


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an LLM provider"""
    result = await db.execute(
        select(LLMProvider).where(LLMProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    await db.delete(provider)
    await db.commit()


# Model endpoints
@router.get("/models", response_model=List[LLMModelResponse])
async def get_models(db: AsyncSession = Depends(get_db)):
    """Get all LLM models"""
    result = await db.execute(
        select(LLMModel).options(joinedload(LLMModel.provider))
    )
    models = result.scalars().all()
    return models


@router.get("/models/active", response_model=List[LLMModelActiveResponse])
async def get_active_models(db: AsyncSession = Depends(get_db)):
    """Get all active LLM models for dropdown selection"""
    result = await db.execute(
        select(LLMModel, LLMProvider)
        .join(LLMProvider)
        .where(LLMModel.is_active == True, LLMProvider.is_active == True)
    )

    active_models = []
    for model, provider in result:
        active_models.append(LLMModelActiveResponse(
            id=model.id,
            model_name=model.model_name,
            display_name=model.display_name,
            description=model.description,
            provider_name=provider.name,
            provider_type=provider.provider_type
        ))

    return active_models


@router.post("/models", response_model=LLMModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(model: LLMModelCreate, db: AsyncSession = Depends(get_db)):
    """Create a new LLM model"""
    # Check if provider exists
    result = await db.execute(
        select(LLMProvider).where(LLMProvider.id == model.provider_id)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    # Check if model name already exists for this provider
    result = await db.execute(
        select(LLMModel).where(LLMModel.provider_id == model.provider_id, LLMModel.model_name == model.model_name)
    )
    existing_model = result.scalar_one_or_none()
    if existing_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model with this name already exists for this provider"
        )

    db_model = LLMModel(**model.dict())
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)

    # Load provider relationship
    result = await db.execute(
        select(LLMModel).options(joinedload(LLMModel.provider)).where(LLMModel.id == db_model.id)
    )
    db_model = result.scalar_one()

    return db_model


@router.get("/models/{model_id}", response_model=LLMModelResponse)
async def get_model(model_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific LLM model"""
    result = await db.execute(
        select(LLMModel).options(joinedload(LLMModel.provider)).where(LLMModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model


@router.put("/models/{model_id}", response_model=LLMModelResponse)
async def update_model(
    model_id: int,
    model_update: LLMModelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an LLM model"""
    result = await db.execute(
        select(LLMModel).where(LLMModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    # Check if provider exists if provider_id is being updated
    if model_update.provider_id is not None:
        result = await db.execute(
            select(LLMProvider).where(LLMProvider.id == model_update.provider_id)
        )
        provider = result.scalar_one_or_none()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found"
            )

    # Check for name conflicts if model_name is being updated
    if model_update.model_name and model_update.provider_id is not None:
        result = await db.execute(
            select(LLMModel).where(
                LLMModel.provider_id == model_update.provider_id,
                LLMModel.model_name == model_update.model_name,
                LLMModel.id != model_id
            )
        )
        existing_model = result.scalar_one_or_none()
        if existing_model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model with this name already exists for this provider"
            )

    # Update model fields
    for field, value in model_update.dict(exclude_unset=True).items():
        setattr(model, field, value)

    await db.commit()
    await db.refresh(model)

    # Load provider relationship
    result = await db.execute(
        select(LLMModel).options(joinedload(LLMModel.provider)).where(LLMModel.id == model_id)
    )
    model = result.scalar_one()

    return model


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an LLM model"""
    result = await db.execute(
        select(LLMModel).where(LLMModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    await db.delete(model)
    await db.commit()
