"""
收藏路由
处理菜谱收藏、取消收藏、查看收藏列表等操作
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.bookmark import Bookmark
from app.models.tag import Tag, RecipeTag
from app.schemas.bookmark import (
    BookmarkCreate,
    BookmarkResponse,
    BookmarkStatusResponse,
    BookmarkRecipeResponse,
)
from app.schemas.common import PaginatedResponse
from app.core.security import get_current_user

router = APIRouter()


def _parse_uuid(id_str: str, field_name: str = "ID") -> uuid.UUID:
    try:
        return uuid.UUID(id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的{field_name}格式"
        )


def _get_bookmark_count(db: Session, recipe_id: uuid.UUID) -> int:
    return db.query(func.count(Bookmark.id)).filter(
        Bookmark.recipe_id == recipe_id
    ).scalar() or 0


def _is_bookmarked(db: Session, user_id: uuid.UUID, recipe_id: uuid.UUID) -> bool:
    return db.query(Bookmark).filter(
        Bookmark.user_id == user_id,
        Bookmark.recipe_id == recipe_id
    ).first() is not None


# =============================================================================
# 收藏操作
# =============================================================================

@router.post("", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recipe_uuid = bookmark_data.recipe_id

    recipe = db.query(Recipe).filter(Recipe.id == recipe_uuid).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    if recipe.user_id != current_user.id and not recipe.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权收藏此菜谱"
        )

    existing_bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.recipe_id == recipe_uuid
    ).first()

    if existing_bookmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已经收藏过此菜谱"
        )

    new_bookmark = Bookmark(
        user_id=current_user.id,
        recipe_id=recipe_uuid
    )

    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)

    return new_bookmark


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")

    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.recipe_id == recipe_uuid
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到收藏记录"
        )

    db.delete(bookmark)
    db.commit()

    return None


@router.get("/status/{recipe_id}", response_model=BookmarkStatusResponse)
async def get_bookmark_status(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_uuid).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    is_bookmarked = _is_bookmarked(db, current_user.id, recipe_uuid)
    bookmark_count = _get_bookmark_count(db, recipe_uuid)

    return BookmarkStatusResponse(
        is_bookmarked=is_bookmarked,
        bookmark_count=bookmark_count
    )


@router.get("", response_model=PaginatedResponse[BookmarkRecipeResponse])
async def list_bookmarks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    tag_id: Optional[str] = Query(None, description="标签ID筛选"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    min_cooking_time: Optional[int] = Query(None, ge=0, description="最短烹饪时间（分钟）"),
    max_cooking_time: Optional[int] = Query(None, ge=0, description="最长烹饪时间（分钟）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmark_alias = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).subquery("user_bookmarks")

    query = db.query(
        Recipe,
        bookmark_alias.c.created_at.label("bookmarked_at")
    ).join(
        bookmark_alias,
        bookmark_alias.c.recipe_id == Recipe.id
    ).options(
        selectinload(Recipe.tags)
    )

    if search:
        query = query.filter(
            Recipe.title.contains(search) | Recipe.description.contains(search)
        )

    if tag_id:
        tag_uuid = _parse_uuid(tag_id, "标签ID")
        query = query.filter(
            Recipe.recipe_tags.any(RecipeTag.tag_id == tag_uuid)
        )

    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)

    if min_cooking_time is not None:
        query = query.filter(Recipe.cooking_time >= min_cooking_time)
    if max_cooking_time is not None:
        query = query.filter(Recipe.cooking_time <= max_cooking_time)

    total = query.with_entities(func.count(func.distinct(Recipe.id))).scalar() or 0

    bookmarks = query.order_by(bookmark_alias.c.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for recipe, bookmarked_at in bookmarks:
        total_bookmarks = _get_bookmark_count(db, recipe.id)

        tags_list = [
            {
                "id": tag.id,
                "name": tag.name,
                "description": tag.description,
                "color": tag.color,
                "created_at": tag.created_at,
            }
            for tag in recipe.tags
        ]

        recipe_dict = {
            "id": recipe.id,
            "user_id": recipe.user_id,
            "title": recipe.title,
            "description": recipe.description,
            "cover_image": recipe.cover_image,
            "cooking_time": recipe.cooking_time,
            "servings": recipe.servings,
            "difficulty": recipe.difficulty,
            "is_public": recipe.is_public,
            "bookmark_count": total_bookmarks,
            "bookmarked_at": bookmarked_at,
            "tags": tags_list,
        }
        items.append(recipe_dict)

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
