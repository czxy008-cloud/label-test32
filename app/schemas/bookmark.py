"""
收藏相关Schemas
定义收藏创建、响应等数据校验模型
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.tag import TagResponse


class BookmarkCreate(BaseModel):
    """收藏创建模型"""
    recipe_id: uuid.UUID = Field(..., description="菜谱ID")


class BookmarkResponse(BaseModel):
    """收藏响应模型"""
    id: uuid.UUID
    user_id: uuid.UUID
    recipe_id: uuid.UUID
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class BookmarkStatusResponse(BaseModel):
    """收藏状态响应模型"""
    is_bookmarked: bool
    bookmark_count: int


class BookmarkRecipeResponse(BaseModel):
    """收藏的菜谱列表响应模型"""
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    cooking_time: int
    servings: int
    difficulty: str
    is_public: bool
    bookmark_count: int
    bookmarked_at: datetime
    tags: List[TagResponse] = []

    model_config = {
        "from_attributes": True
    }
