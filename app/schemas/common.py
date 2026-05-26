"""
通用Schemas
定义分页、消息等通用响应模型
"""

from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str
    status_code: int = 400


class PaginationParams(BaseModel):
    """分页查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: str = Field(default="desc", description="排序方向: asc/desc")
