"""
购物清单相关Schemas
定义购物清单创建、更新、响应等数据校验模型
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ShoppingListItemBase(BaseModel):
    """购物清单详情基础模型"""
    ingredient_name: str = Field(..., min_length=1, max_length=100, description="食材名称")
    quantity: float = Field(..., gt=0, description="需求量")
    unit: str = Field(..., min_length=1, max_length=20, description="计量单位")
    is_purchased: bool = Field(default=False, description="是否已购买")
    notes: Optional[str] = Field(None, description="备注")


class ShoppingListItemCreate(ShoppingListItemBase):
    """购物清单详情创建模型"""
    pass


class ShoppingListItemUpdate(BaseModel):
    """购物清单详情更新模型"""
    ingredient_name: Optional[str] = Field(None, min_length=1, max_length=100, description="食材名称")
    quantity: Optional[float] = Field(None, gt=0, description="需求量")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="计量单位")
    is_purchased: Optional[bool] = Field(None, description="是否已购买")
    notes: Optional[str] = Field(None, description="备注")


class ShoppingListItemResponse(ShoppingListItemBase):
    """购物清单详情响应模型"""
    id: uuid.UUID
    shopping_list_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ShoppingListBase(BaseModel):
    """购物清单基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="清单名称")
    is_completed: bool = Field(default=False, description="是否已完成")


class ShoppingListCreate(ShoppingListBase):
    """购物清单创建模型"""
    meal_plan_id: uuid.UUID = Field(..., description="关联饮食计划ID")


class ShoppingListUpdate(BaseModel):
    """购物清单更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="清单名称")
    is_completed: Optional[bool] = Field(None, description="是否已完成")


class ShoppingListResponse(ShoppingListBase):
    """购物清单响应模型"""
    id: uuid.UUID
    meal_plan_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ShoppingListWithItems(ShoppingListResponse):
    """购物清单含详情响应模型"""
    items: List[ShoppingListItemResponse] = []
