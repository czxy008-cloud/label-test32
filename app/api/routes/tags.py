"""
标签路由
处理标签的创建、查询等操作
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse
from app.core.security import get_current_user

router = APIRouter()


def _parse_uuid(id_str: str, field_name: str = "ID") -> uuid.UUID:
    """将字符串转换为UUID"""
    try:
        return uuid.UUID(id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的{field_name}格式"
        )


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新标签

    - 标签名称必须唯一
    """
    # 检查标签是否已存在
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该标签已存在"
        )

    new_tag = Tag(
        name=tag_data.name,
        description=tag_data.description,
        color=tag_data.color,
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


@router.get("", response_model=List[TagResponse])
async def list_tags(
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有标签列表

    - 支持搜索
    """
    query = db.query(Tag)

    if search:
        query = query.filter(Tag.name.contains(search))

    tags = query.order_by(Tag.name).all()

    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取标签详情
    """
    tag_uuid = _parse_uuid(tag_id, "标签ID")
    tag = db.query(Tag).filter(Tag.id == tag_uuid).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新标签信息
    """
    tag_uuid = _parse_uuid(tag_id, "标签ID")
    tag = db.query(Tag).filter(Tag.id == tag_uuid).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    # 检查名称唯一性
    if tag_data.name != tag.name:
        existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该标签名称已存在"
            )

    tag.name = tag_data.name
    tag.description = tag_data.description
    tag.color = tag_data.color

    db.commit()
    db.refresh(tag)

    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除标签

    - 会级联删除所有菜谱与该标签的关联
    """
    tag_uuid = _parse_uuid(tag_id, "标签ID")
    tag = db.query(Tag).filter(Tag.id == tag_uuid).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    db.delete(tag)
    db.commit()

    return None
