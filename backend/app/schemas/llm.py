from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime


def infer_provider_type(model_name: str) -> Optional[str]:
    """Infer provider type from model name (extract part before '/')"""
    if '/' in model_name:
        return model_name.split('/')[0]
    return None


# LLM Model Schemas
class LLMModelBase(BaseModel):
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    provider_type: Optional[str] = None
    is_active: bool = True

    @model_validator(mode='before')
    @classmethod
    def auto_infer_provider_type(cls, data):
        """Auto-infer provider_type from model_name if not provided"""
        if isinstance(data, dict):
            if data.get('provider_type') is None and data.get('model_name'):
                data['provider_type'] = infer_provider_type(data['model_name'])
        return data


class LLMModelCreate(LLMModelBase):
    pass


class LLMModelUpdate(BaseModel):
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    provider_type: Optional[str] = None
    is_active: Optional[bool] = None

    @model_validator(mode='before')
    @classmethod
    def auto_infer_provider_type(cls, data):
        """Auto-infer provider_type from model_name if not provided"""
        if isinstance(data, dict):
            if data.get('provider_type') is None and data.get('model_name'):
                data['provider_type'] = infer_provider_type(data['model_name'])
        return data


class LLMModelResponse(LLMModelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LLMModelActiveResponse(BaseModel):
    id: int
    model_name: str
    provider_type: Optional[str] = None

    class Config:
        from_attributes = True

class LLMModelPublicResponse(BaseModel):
    id: int
    model_name: str
    base_url: Optional[str] = None
    provider_type: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

