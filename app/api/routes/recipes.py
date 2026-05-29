"""
菜谱路由
处理菜谱的创建、查询、更新、删除等操作
支持多步骤图文混排和标签分类
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe, RecipeStep, RecipeIngredient
from app.models.tag import Tag, RecipeTag
from app.models.bookmark import Bookmark
from app.schemas.recipe import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeListResponse,
    RecipeStepCreate,
    RecipeStepUpdate,
    RecipeStepResponse,
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
    RecipeIngredientResponse,
    RecipeWithBookmarkResponse,
)
from app.core.security import get_current_user

router = APIRouter()


def _get_bookmark_count(db: Session, recipe_id: uuid.UUID) -> int:
    return db.query(func.count(Bookmark.id)).filter(
        Bookmark.recipe_id == recipe_id
    ).scalar() or 0


def _is_bookmarked(db: Session, user_id: uuid.UUID, recipe_id: uuid.UUID) -> bool:
    return db.query(Bookmark).filter(
        Bookmark.user_id == user_id,
        Bookmark.recipe_id == recipe_id
    ).first() is not None


def _parse_uuid(id_str: str, field_name: str = "ID") -> uuid.UUID:
    try:
        return uuid.UUID(id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的{field_name}格式"
        )


# =============================================================================
# 菜谱CRUD
# =============================================================================

@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_recipe = Recipe(
        user_id=current_user.id,
        title=recipe_data.title,
        description=recipe_data.description,
        cover_image=recipe_data.cover_image,
        cooking_time=recipe_data.cooking_time,
        servings=recipe_data.servings,
        difficulty=recipe_data.difficulty,
        is_public=recipe_data.is_public,
    )

    db.add(new_recipe)
    db.flush()

    for step_data in recipe_data.steps:
        step = RecipeStep(
            recipe_id=new_recipe.id,
            step_number=step_data.step_number,
            description=step_data.description,
            image_url=step_data.image_url,
        )
        db.add(step)

    for ing_data in recipe_data.ingredients:
        ingredient = RecipeIngredient(
            recipe_id=new_recipe.id,
            ingredient_id=ing_data.ingredient_id if ing_data.ingredient_id else None,
            ingredient_name=ing_data.ingredient_name,
            quantity=ing_data.quantity,
            unit=ing_data.unit,
        )
        db.add(ingredient)

    for tag_id in recipe_data.tag_ids:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag:
            recipe_tag = RecipeTag(recipe_id=new_recipe.id, tag_id=tag.id)
            db.add(recipe_tag)

    db.commit()
    db.refresh(new_recipe)

    return new_recipe


@router.get("", response_model=List[RecipeListResponse])
async def list_recipes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    tag_id: Optional[str] = Query(None, description="标签ID筛选"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    is_public: Optional[bool] = Query(None, description="是否公开"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Recipe).options(selectinload(Recipe.tags))

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

    if is_public is not None:
        if is_public:
            query = query.filter(Recipe.is_public == True)
        else:
            query = query.filter(
                (Recipe.user_id == current_user.id) & (Recipe.is_public == False)
            )
    else:
        query = query.filter(
            (Recipe.user_id == current_user.id) | (Recipe.is_public == True)
        )

    total = query.with_entities(func.count(func.distinct(Recipe.id))).scalar() or 0

    recipes = query.order_by(Recipe.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return recipes


@router.get("/{recipe_id}", response_model=RecipeWithBookmarkResponse)
async def get_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")
    recipe = db.query(Recipe).options(
        selectinload(Recipe.tags),
        selectinload(Recipe.steps),
        selectinload(Recipe.ingredients),
    ).filter(Recipe.id == recipe_uuid).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    if recipe.user_id != current_user.id and not recipe.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此菜谱"
        )

    is_bookmarked = _is_bookmarked(db, current_user.id, recipe_uuid)
    bookmark_count = _get_bookmark_count(db, recipe_uuid)

    recipe_data = {
        "id": recipe.id,
        "user_id": recipe.user_id,
        "title": recipe.title,
        "description": recipe.description,
        "cover_image": recipe.cover_image,
        "cooking_time": recipe.cooking_time,
        "servings": recipe.servings,
        "difficulty": recipe.difficulty,
        "is_public": recipe.is_public,
        "steps": recipe.steps,
        "ingredients": recipe.ingredients,
        "tags": recipe.tags,
        "bookmark_count": bookmark_count,
        "is_bookmarked": is_bookmarked,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
    }

    return recipe_data


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    recipe_data: RecipeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新菜谱信息

    - 只有菜谱所有者可以更新
    """
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")
    recipe = db.query(Recipe).filter(Recipe.id == recipe_uuid).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    # 检查权限
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此菜谱"
        )

    # 更新基本信息
    if recipe_data.title is not None:
        recipe.title = recipe_data.title
    if recipe_data.description is not None:
        recipe.description = recipe_data.description
    if recipe_data.cover_image is not None:
        recipe.cover_image = recipe_data.cover_image
    if recipe_data.cooking_time is not None:
        recipe.cooking_time = recipe_data.cooking_time
    if recipe_data.servings is not None:
        recipe.servings = recipe_data.servings
    if recipe_data.difficulty is not None:
        recipe.difficulty = recipe_data.difficulty
    if recipe_data.is_public is not None:
        recipe.is_public = recipe_data.is_public

    # 更新标签（完整替换）
    if recipe_data.tag_ids is not None:
        # 删除旧标签关联
        db.query(RecipeTag).filter(RecipeTag.recipe_id == recipe.id).delete()
        # 添加新标签关联
        for tag_id in recipe_data.tag_ids:
            tag = db.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                recipe_tag = RecipeTag(recipe_id=recipe.id, tag_id=tag.id)
                db.add(recipe_tag)

    db.commit()
    db.refresh(recipe)

    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除菜谱

    - 只有菜谱所有者可以删除
    """
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")
    recipe = db.query(Recipe).filter(Recipe.id == recipe_uuid).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    # 检查权限
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此菜谱"
        )

    db.delete(recipe)
    db.commit()

    return None


# =============================================================================
# 步骤管理
# =============================================================================

@router.post("/{recipe_id}/steps", response_model=RecipeStepResponse)
async def add_recipe_step(
    recipe_id: str,
    step_data: RecipeStepCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为菜谱添加步骤

    - 支持图文混排
    """
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")
    recipe = db.query(Recipe).filter(Recipe.id == recipe_uuid).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此菜谱"
        )

    # 检查步骤序号是否冲突
    existing_step = db.query(RecipeStep).filter(
        RecipeStep.recipe_id == recipe_uuid,
        RecipeStep.step_number == step_data.step_number
    ).first()

    if existing_step:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该步骤序号已存在"
        )

    new_step = RecipeStep(
        recipe_id=recipe_uuid,
        step_number=step_data.step_number,
        description=step_data.description,
        image_url=step_data.image_url,
    )

    db.add(new_step)
    db.commit()
    db.refresh(new_step)

    return new_step


@router.put("/steps/{step_id}", response_model=RecipeStepResponse)
async def update_recipe_step(
    step_id: str,
    step_data: RecipeStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新菜谱步骤
    """
    step_uuid = _parse_uuid(step_id, "步骤ID")
    step = db.query(RecipeStep).filter(RecipeStep.id == step_uuid).first()

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="步骤不存在"
        )

    recipe = db.query(Recipe).filter(Recipe.id == step.recipe_id).first()
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此菜谱"
        )

    if step_data.step_number is not None:
        step.step_number = step_data.step_number
    if step_data.description is not None:
        step.description = step_data.description
    if step_data.image_url is not None:
        step.image_url = step_data.image_url

    db.commit()
    db.refresh(step)

    return step


@router.delete("/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_step(
    step_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除菜谱步骤
    """
    step_uuid = _parse_uuid(step_id, "步骤ID")
    step = db.query(RecipeStep).filter(RecipeStep.id == step_uuid).first()

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="步骤不存在"
        )

    recipe = db.query(Recipe).filter(Recipe.id == step.recipe_id).first()
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此菜谱"
        )

    db.delete(step)
    db.commit()

    return None


# =============================================================================
# 食材管理
# =============================================================================

@router.post("/{recipe_id}/ingredients", response_model=RecipeIngredientResponse)
async def add_recipe_ingredient(
    recipe_id: str,
    ingredient_data: RecipeIngredientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为菜谱添加食材
    """
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")
    recipe = db.query(Recipe).filter(Recipe.id == recipe_uuid).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此菜谱"
        )

    new_ingredient = RecipeIngredient(
        recipe_id=recipe_uuid,
        ingredient_id=ingredient_data.ingredient_id if ingredient_data.ingredient_id else None,
        ingredient_name=ingredient_data.ingredient_name,
        quantity=ingredient_data.quantity,
        unit=ingredient_data.unit,
    )

    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)

    return new_ingredient


@router.put("/ingredients/{ingredient_id}", response_model=RecipeIngredientResponse)
async def update_recipe_ingredient(
    ingredient_id: str,
    ingredient_data: RecipeIngredientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新菜谱食材
    """
    ing_uuid = _parse_uuid(ingredient_id, "食材ID")
    ingredient = db.query(RecipeIngredient).filter(RecipeIngredient.id == ing_uuid).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食材不存在"
        )

    recipe = db.query(Recipe).filter(Recipe.id == ingredient.recipe_id).first()
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此菜谱"
        )

    if ingredient_data.ingredient_name is not None:
        ingredient.ingredient_name = ingredient_data.ingredient_name
    if ingredient_data.quantity is not None:
        ingredient.quantity = ingredient_data.quantity
    if ingredient_data.unit is not None:
        ingredient.unit = ingredient_data.unit
    if ingredient_data.ingredient_id is not None:
        ingredient.ingredient_id = ingredient_data.ingredient_id

    db.commit()
    db.refresh(ingredient)

    return ingredient


@router.delete("/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_ingredient(
    ingredient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除菜谱食材
    """
    ing_uuid = _parse_uuid(ingredient_id, "食材ID")
    ingredient = db.query(RecipeIngredient).filter(RecipeIngredient.id == ing_uuid).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食材不存在"
        )

    recipe = db.query(Recipe).filter(Recipe.id == ingredient.recipe_id).first()
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此菜谱"
        )

    db.delete(ingredient)
    db.commit()

    return None
