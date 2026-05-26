"""
用户路由
处理用户信息查询和更新
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.core.security import get_current_user, hash_password, verify_password

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    获取当前用户个人信息
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户个人信息

    - 可更新姓名、头像
    - 修改密码需要提供旧密码
    """
    # 更新基本信息
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name

    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url

    # 修改密码
    if user_data.new_password:
        # 验证旧密码
        if not user_data.old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="修改密码需要提供旧密码"
            )

        if not verify_password(user_data.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码不正确"
            )

        current_user.password_hash = hash_password(user_data.new_password)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除当前用户账号

    - 会级联删除所有相关数据（菜谱、饮食计划等）
    - 此操作不可恢复
    """
    db.delete(current_user)
    db.commit()

    return None
