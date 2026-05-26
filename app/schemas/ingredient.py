"""
食材相关Schemas
定义食材创建、更新、响应等数据校验模型
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class IngredientBase(BaseModel):
    """食材基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="食材名称")
    category: str = Field(..., min_length=1, max_length=50, description="食材分类")
    unit: str = Field(default="g", min_length=1, max_length=20, description="计量单位")
    calories: float = Field(default=0, ge=0, description="每单位热量")
    protein: float = Field(default=0, ge=0, description="每单位蛋白质含量")
    fat: float = Field(default=0, ge=0, description="每单位脂肪含量")
    carbohydrates: float = Field(default=0, ge=0, description="每单位碳水化合物含量")
    description: Optional[str] = Field(None, description="食材描述")


class IngredientCreate(IngredientBase):
    """食材创建模型"""
    pass


class IngredientUpdate(BaseModel):
    """食材更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="食材名称")
    category: Optional[str] = Field(None, min_length=1, max_length=50, description="食材分类")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="计量单位")
    calories: Optional[float] = Field(None, ge=0, description="每单位热量")
    protein: Optional[float] = Field(None, ge=0, description="每单位蛋白质含量")
    fat: Optional[float] = Field(None, ge=0, description="每单位脂肪含量")
    carbohydrates: Optional[float] = Field(None, ge=0, description="每单位碳水化合物含量")
    description: Optional[str] = Field(None, description="食材描述")


class IngredientResponse(IngredientBase):
    """食材响应模型"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class NutritionInfo(BaseModel):
    """营养信息模型"""
    total_calories: float = 0.0
    total_protein: float = 0.0
    total_fat: float = 0.0
    total_carbohydrates: float = 0.0
    per_serving_calories: float = 0.0
    per_serving_protein: float = 0.0
    per_serving_fat: float = 0.0
    per_serving_carbohydrates: float = 0.0
    servings: int = 1
    details: list = []
