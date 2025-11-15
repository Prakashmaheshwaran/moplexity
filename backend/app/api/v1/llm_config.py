from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.core.database import get_db
from app.models import LLMModel
from app.schemas import (
    LLMModelCreate,
    LLMModelUpdate,
    LLMModelResponse,
    LLMModelActiveResponse
)
from app.schemas.llm import infer_provider_type, LLMModelPublicResponse
from app.core.config import settings

router = APIRouter()


# Model endpoints
@router.get("/models", response_model=List[LLMModelPublicResponse])
async def get_models(db: AsyncSession = Depends(get_db)):
    """Get all LLM models"""
    result = await db.execute(
        select(LLMModel).order_by(LLMModel.created_at.desc())
    )
    models = result.scalars().all()
    return models


@router.get("/models/active", response_model=List[LLMModelActiveResponse])
async def get_active_models(db: AsyncSession = Depends(get_db)):
    """Get all active LLM models for dropdown selection"""
    result = await db.execute(
        select(LLMModel)
        .where(LLMModel.is_active == True)
        .order_by(LLMModel.model_name)
    )
    models = result.scalars().all()
    return models


def _require_admin(authorization: Optional[str]):
    # If admin token is configured, require matching Bearer token; otherwise allow
    admin_token = getattr(settings, 'admin_token', None)
    if not admin_token:
        return
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if token == admin_token:
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

@router.post("/models", response_model=LLMModelPublicResponse, status_code=status.HTTP_201_CREATED)
async def create_model(model: LLMModelCreate, db: AsyncSession = Depends(get_db), authorization: Optional[str] = Header(None)):
    _require_admin(authorization)
    """Create a new LLM model"""
    # Check if model name already exists
    result = await db.execute(
        select(LLMModel).where(LLMModel.model_name == model.model_name)
    )
    existing_model = result.scalar_one_or_none()
    if existing_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model with this name already exists"
        )

    # Auto-infer provider_type if not provided
    model_data = model.dict()
    if not model_data.get('provider_type') and model_data.get('model_name'):
        model_data['provider_type'] = infer_provider_type(model_data['model_name'])

    db_model = LLMModel(**model_data)
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)

    return db_model


@router.get("/models/{model_id}", response_model=LLMModelPublicResponse)
async def get_model(model_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific LLM model"""
    result = await db.execute(
        select(LLMModel).where(LLMModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model


@router.put("/models/{model_id}", response_model=LLMModelPublicResponse)
async def update_model(
    model_id: int,
    model_update: LLMModelUpdate,
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    _require_admin(authorization)
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

    # Check for name conflicts if model_name is being updated
    update_data = model_update.dict(exclude_unset=True)
    if 'model_name' in update_data:
        # Auto-infer provider_type if model_name changed and provider_type not explicitly set
        if 'provider_type' not in update_data:
            inferred_provider = infer_provider_type(update_data['model_name'])
            if inferred_provider:
                update_data['provider_type'] = inferred_provider
        
        result = await db.execute(
            select(LLMModel).where(
                LLMModel.model_name == update_data['model_name'],
                LLMModel.id != model_id
            )
        )
        existing_model = result.scalar_one_or_none()
        if existing_model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model with this name already exists"
            )

    # Update model fields
    for field, value in update_data.items():
        setattr(model, field, value)

    await db.commit()
    await db.refresh(model)

    return model


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: int, db: AsyncSession = Depends(get_db), authorization: Optional[str] = Header(None)):
    _require_admin(authorization)
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
