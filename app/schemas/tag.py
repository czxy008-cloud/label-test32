"""
标签相关Schemas
定义标签创建、响应等数据校验模型
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    description: Optional[str] = Field(None, max_length=500, description="标签描述")
    color: Optional[str] = Field(default="#1890ff", max_length=20, description="标签颜色")


class TagCreate(TagBase):
    """标签创建模型"""
    pass


class TagResponse(TagBase):
    """标签响应模型"""
    id: uuid.UUID
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TagWithRecipes(TagResponse):
    """标签含菜谱统计"""
    recipe_count: int = 0
