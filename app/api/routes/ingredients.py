"""
食材路由
处理食材营养信息的CRUD操作
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientResponse
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


@router.post("", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    ingredient_data: IngredientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新食材

    - 食材名称必须唯一
    - 包含基础营养信息（热量、蛋白质、脂肪、碳水化合物）
    """
    # 检查食材是否已存在
    existing_ingredient = db.query(Ingredient).filter(Ingredient.name == ingredient_data.name).first()
    if existing_ingredient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该食材已存在"
        )

    new_ingredient = Ingredient(
        name=ingredient_data.name,
        category=ingredient_data.category,
        unit=ingredient_data.unit,
        calories=ingredient_data.calories,
        protein=ingredient_data.protein,
        fat=ingredient_data.fat,
        carbohydrates=ingredient_data.carbohydrates,
        description=ingredient_data.description,
    )

    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)

    return new_ingredient


@router.get("", response_model=List[IngredientResponse])
async def list_ingredients(
    category: Optional[str] = Query(None, description="食材分类筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取食材列表

    - 支持按分类筛选
    - 支持搜索
    """
    query = db.query(Ingredient)

    if category:
        query = query.filter(Ingredient.category == category)

    if search:
        query = query.filter(Ingredient.name.contains(search))

    ingredients = query.order_by(Ingredient.name).all()

    return ingredients


@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient(
    ingredient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取食材详情
    """
    ingredient_uuid = _parse_uuid(ingredient_id, "食材ID")
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_uuid).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食材不存在"
        )

    return ingredient


@router.put("/{ingredient_id}", response_model=IngredientResponse)
async def update_ingredient(
    ingredient_id: str,
    ingredient_data: IngredientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新食材信息
    """
    ingredient_uuid = _parse_uuid(ingredient_id, "食材ID")
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_uuid).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食材不存在"
        )

    # 更新信息
    update_data = ingredient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)

    return ingredient


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除食材
    """
    ingredient_uuid = _parse_uuid(ingredient_id, "食材ID")
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_uuid).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食材不存在"
        )

    db.delete(ingredient)
    db.commit()

    return None


@router.get("/categories/list", response_model=List[str])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有食材分类列表
    """
    categories = db.query(Ingredient.category).distinct().all()
    return [cat[0] for cat in categories]
