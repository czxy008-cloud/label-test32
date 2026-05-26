"""
菜谱相关Schemas
定义菜谱创建、更新、响应等数据校验模型
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class RecipeStepBase(BaseModel):
    """步骤基础模型"""
    step_number: int = Field(..., ge=1, description="步骤序号")
    description: str = Field(..., min_length=1, description="步骤描述")
    image_url: Optional[str] = Field(None, max_length=500, description="步骤配图URL")


class RecipeStepCreate(RecipeStepBase):
    """步骤创建模型"""
    pass


class RecipeStepUpdate(BaseModel):
    """步骤更新模型"""
    step_number: Optional[int] = Field(None, ge=1, description="步骤序号")
    description: Optional[str] = Field(None, min_length=1, description="步骤描述")
    image_url: Optional[str] = Field(None, max_length=500, description="步骤配图URL")


class RecipeStepResponse(RecipeStepBase):
    """步骤响应模型"""
    id: uuid.UUID
    recipe_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class RecipeIngredientBase(BaseModel):
    """食材基础模型"""
    ingredient_name: str = Field(..., min_length=1, max_length=100, description="食材名称")
    quantity: float = Field(..., gt=0, description="用量")
    unit: str = Field(..., min_length=1, max_length=20, description="计量单位")
    ingredient_id: Optional[uuid.UUID] = Field(None, description="关联食材库ID")


class RecipeIngredientCreate(RecipeIngredientBase):
    """食材创建模型"""
    pass


class RecipeIngredientUpdate(BaseModel):
    """食材更新模型"""
    ingredient_name: Optional[str] = Field(None, min_length=1, max_length=100, description="食材名称")
    quantity: Optional[float] = Field(None, gt=0, description="用量")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="计量单位")
    ingredient_id: Optional[uuid.UUID] = Field(None, description="关联食材库ID")


class RecipeIngredientResponse(RecipeIngredientBase):
    """食材响应模型"""
    id: uuid.UUID
    recipe_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class RecipeBase(BaseModel):
    """菜谱基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="菜谱标题")
    description: Optional[str] = Field(None, description="菜谱描述")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片URL")
    cooking_time: int = Field(default=0, ge=0, description="烹饪时间（分钟）")
    servings: int = Field(default=1, ge=1, description="份量")
    difficulty: str = Field(default="easy", description="难度等级: easy/medium/hard")
    is_public: bool = Field(default=False, description="是否公开")

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """验证难度等级"""
        valid_levels = ["easy", "medium", "hard"]
        if v not in valid_levels:
            raise ValueError(f"难度等级必须是: {', '.join(valid_levels)}")
        return v


class RecipeCreate(RecipeBase):
    """菜谱创建模型"""
    steps: List[RecipeStepCreate] = Field(default_factory=list, description="烹饪步骤列表")
    ingredients: List[RecipeIngredientCreate] = Field(default_factory=list, description="食材列表")
    tag_ids: List[uuid.UUID] = Field(default_factory=list, description="标签ID列表")


class RecipeUpdate(BaseModel):
    """菜谱更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="菜谱标题")
    description: Optional[str] = Field(None, description="菜谱描述")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片URL")
    cooking_time: Optional[int] = Field(None, ge=0, description="烹饪时间（分钟）")
    servings: Optional[int] = Field(None, ge=1, description="份量")
    difficulty: Optional[str] = Field(None, description="难度等级")
    is_public: Optional[bool] = Field(None, description="是否公开")
    tag_ids: Optional[List[uuid.UUID]] = Field(None, description="标签ID列表（完整替换）")


class RecipeResponse(RecipeBase):
    """菜谱响应模型"""
    id: uuid.UUID
    user_id: uuid.UUID
    steps: List[RecipeStepResponse] = []
    ingredients: List[RecipeIngredientResponse] = []
    tags: List = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class RecipeListResponse(BaseModel):
    """菜谱列表响应模型（精简版）"""
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    cooking_time: int
    servings: int
    difficulty: str
    is_public: bool
    tags: List = []
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
