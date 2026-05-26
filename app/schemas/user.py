"""
用户相关Schemas
定义用户注册、登录、更新等数据校验模型
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="用户邮箱地址")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")


class UserCreate(UserBase):
    """用户注册请求模型"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="用户密码（至少8位，需包含字母和数字）"
    )
    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="确认密码"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码复杂度"""
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("密码必须包含至少一个字母")
        if not re.search(r'[0-9]', v):
            raise ValueError("密码必须包含至少一个数字")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info) -> str:
        """验证两次密码一致"""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        return v


class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr = Field(..., description="用户邮箱地址")
    password: str = Field(..., description="用户密码")
    remember_me: bool = Field(default=False, description="是否记住我（延长登录有效期）")


class LoginRequest(BaseModel):
    """登录请求（兼容username/email登录）"""
    login: str = Field(..., description="邮箱或用户名")
    password: str = Field(..., description="用户密码")
    remember_me: bool = Field(default=False, description="是否记住我")


class UserUpdate(BaseModel):
    """用户更新请求模型"""
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    old_password: Optional[str] = Field(None, description="当前密码（修改密码时需要）")
    new_password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="新密码（至少8位，需包含字母和数字）"
    )


class UserResponse(BaseModel):
    """用户响应模型"""
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserWithToken(BaseModel):
    """用户信息含Token"""
    user: UserResponse
    token: TokenResponse
