"""
饮食计划相关Schemas
定义饮食计划创建、更新、响应等数据校验模型
"""

import uuid
from datetime import datetime, date as date_type
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class MealPlanItemBase(BaseModel):
    """饮食计划详情基础模型"""
    date: date_type = Field(..., description="计划日期")
    meal_type: str = Field(..., description="餐类型: breakfast/lunch/dinner/snack")
    recipe_id: Optional[uuid.UUID] = Field(None, description="关联菜谱ID")
    custom_recipe_name: Optional[str] = Field(None, max_length=200, description="自定义菜名")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        """验证餐类型"""
        valid_types = ["breakfast", "lunch", "dinner", "snack"]
        if v not in valid_types:
            raise ValueError(f"餐类型必须是: {', '.join(valid_types)}")
        return v


class MealPlanItemCreate(MealPlanItemBase):
    """饮食计划详情创建模型"""
    pass


class MealPlanItemUpdate(BaseModel):
    """饮食计划详情更新模型"""
    date: Optional[date_type] = Field(None, description="计划日期")
    meal_type: Optional[str] = Field(None, description="餐类型")
    recipe_id: Optional[uuid.UUID] = Field(None, description="关联菜谱ID")
    custom_recipe_name: Optional[str] = Field(None, max_length=200, description="自定义菜名")
    notes: Optional[str] = Field(None, description="备注")


class MealPlanItemResponse(MealPlanItemBase):
    """饮食计划详情响应模型"""
    id: uuid.UUID
    meal_plan_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MealPlanBase(BaseModel):
    """饮食计划基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="计划名称")
    start_date: date_type = Field(..., description="计划开始日期")
    end_date: date_type = Field(..., description="计划结束日期")
    notes: Optional[str] = Field(None, description="计划备注")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: date_type, info) -> date_type:
        """验证日期范围"""
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("结束日期不能早于开始日期")
        return v


class MealPlanCreate(MealPlanBase):
    """饮食计划创建模型"""
    items: List[MealPlanItemCreate] = Field(default_factory=list, description="计划详情列表")


class MealPlanUpdate(BaseModel):
    """饮食计划更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="计划名称")
    start_date: Optional[date_type] = Field(None, description="计划开始日期")
    end_date: Optional[date_type] = Field(None, description="计划结束日期")
    notes: Optional[str] = Field(None, description="计划备注")


class MealPlanResponse(MealPlanBase):
    """饮食计划响应模型"""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MealPlanWithDetails(MealPlanResponse):
    """饮食计划含详情响应模型"""
    items: List[MealPlanItemResponse] = []
