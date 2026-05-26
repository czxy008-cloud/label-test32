"""
饮食计划路由
处理饮食计划的创建、查询、更新、删除等操作
支持按周安排每日三餐
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from collections import defaultdict

from app.database import get_db
from app.models.user import User
from app.models.meal_plan import MealPlan, MealPlanItem
from app.models.recipe import Recipe, RecipeIngredient
from app.models.shopping import ShoppingList, ShoppingListItem
from app.schemas.meal_plan import (
    MealPlanCreate,
    MealPlanUpdate,
    MealPlanResponse,
    MealPlanItemCreate,
    MealPlanItemUpdate,
    MealPlanItemResponse,
    MealPlanWithDetails,
)
from app.schemas.shopping import (
    ShoppingListCreate,
    ShoppingListResponse,
    ShoppingListWithItems,
)
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


# =============================================================================
# 饮食计划CRUD
# =============================================================================

@router.post("", response_model=MealPlanWithDetails, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    plan_data: MealPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建饮食计划

    - 支持按周安排每日三餐
    - 可关联已有菜谱或使用自定义菜名
    """
    # 创建饮食计划
    new_plan = MealPlan(
        user_id=current_user.id,
        name=plan_data.name,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        notes=plan_data.notes,
    )

    db.add(new_plan)
    db.flush()

    # 添加计划项
    for item_data in plan_data.items:
        item = MealPlanItem(
            meal_plan_id=new_plan.id,
            recipe_id=item_data.recipe_id,
            date=item_data.date,
            meal_type=item_data.meal_type,
            custom_recipe_name=item_data.custom_recipe_name,
            notes=item_data.notes,
        )
        db.add(item)

    db.commit()
    db.refresh(new_plan)

    return new_plan


@router.get("", response_model=List[MealPlanResponse])
async def list_meal_plans(
    start_date: Optional[date] = Query(None, description="开始日期筛选"),
    end_date: Optional[date] = Query(None, description="结束日期筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的饮食计划列表

    - 支持按日期范围筛选
    """
    query = db.query(MealPlan).filter(MealPlan.user_id == current_user.id)

    if start_date:
        query = query.filter(MealPlan.end_date >= start_date)
    if end_date:
        query = query.filter(MealPlan.start_date <= end_date)

    plans = query.order_by(MealPlan.created_at.desc()).all()

    return plans


@router.get("/{plan_id}", response_model=MealPlanWithDetails)
async def get_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取饮食计划详情

    - 包含所有计划项
    """
    plan_uuid = _parse_uuid(plan_id, "计划ID")
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_uuid,
        MealPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="饮食计划不存在"
        )

    return plan


@router.put("/{plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    plan_id: str,
    plan_data: MealPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新饮食计划信息
    """
    plan_uuid = _parse_uuid(plan_id, "计划ID")
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_uuid,
        MealPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="饮食计划不存在"
        )

    if plan_data.name is not None:
        plan.name = plan_data.name
    if plan_data.start_date is not None:
        plan.start_date = plan_data.start_date
    if plan_data.end_date is not None:
        plan.end_date = plan_data.end_date
    if plan_data.notes is not None:
        plan.notes = plan_data.notes

    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除饮食计划

    - 会级联删除关联的购物清单
    """
    plan_uuid = _parse_uuid(plan_id, "计划ID")
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_uuid,
        MealPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="饮食计划不存在"
        )

    db.delete(plan)
    db.commit()

    return None


# =============================================================================
# 计划项管理
# =============================================================================

@router.post("/{plan_id}/items", response_model=MealPlanItemResponse)
async def add_meal_plan_item(
    plan_id: str,
    item_data: MealPlanItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为饮食计划添加餐项

    - 支持关联菜谱或使用自定义菜名
    """
    plan_uuid = _parse_uuid(plan_id, "计划ID")
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_uuid,
        MealPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="饮食计划不存在"
        )

    new_item = MealPlanItem(
        meal_plan_id=plan_uuid,
        recipe_id=item_data.recipe_id,
        date=item_data.date,
        meal_type=item_data.meal_type,
        custom_recipe_name=item_data.custom_recipe_name,
        notes=item_data.notes,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.put("/items/{item_id}", response_model=MealPlanItemResponse)
async def update_meal_plan_item(
    item_id: str,
    item_data: MealPlanItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新饮食计划项
    """
    item_uuid = _parse_uuid(item_id, "计划项ID")
    item = db.query(MealPlanItem).filter(MealPlanItem.id == item_uuid).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划项不存在"
        )

    plan = db.query(MealPlan).filter(
        MealPlan.id == item.meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此计划"
        )

    if item_data.date is not None:
        item.date = item_data.date
    if item_data.meal_type is not None:
        item.meal_type = item_data.meal_type
    if item_data.recipe_id is not None:
        item.recipe_id = item_data.recipe_id
    if item_data.custom_recipe_name is not None:
        item.custom_recipe_name = item_data.custom_recipe_name
    if item_data.notes is not None:
        item.notes = item_data.notes

    db.commit()
    db.refresh(item)

    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除饮食计划项
    """
    item_uuid = _parse_uuid(item_id, "计划项ID")
    item = db.query(MealPlanItem).filter(MealPlanItem.id == item_uuid).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划项不存在"
        )

    plan = db.query(MealPlan).filter(
        MealPlan.id == item.meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此计划"
        )

    db.delete(item)
    db.commit()

    return None


# =============================================================================
# 购物清单生成
# =============================================================================

@router.post("/{plan_id}/generate-shopping-list", response_model=ShoppingListWithItems)
async def generate_shopping_list(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据饮食计划自动生成购物清单

    - 汇总计划中所有菜谱的食材
    - 相同食材自动合并数量
    """
    plan_uuid = _parse_uuid(plan_id, "计划ID")
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_uuid,
        MealPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="饮食计划不存在"
        )

    # 获取所有计划项
    plan_items = db.query(MealPlanItem).filter(
        MealPlanItem.meal_plan_id == plan_uuid
    ).all()

    # 汇总所有食材
    ingredient_summary = defaultdict(lambda: {"quantity": 0, "unit": ""})

    for item in plan_items:
        if item.recipe_id:
            # 获取菜谱的食材
            recipe_ingredients = db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == item.recipe_id
            ).all()

            for ri in recipe_ingredients:
                key = f"{ri.ingredient_name}_{ri.unit}"
                ingredient_summary[key]["quantity"] += float(ri.quantity)
                ingredient_summary[key]["unit"] = ri.unit
                ingredient_summary[key]["name"] = ri.ingredient_name

    # 创建购物清单
    shopping_list = ShoppingList(
        meal_plan_id=plan_uuid,
        user_id=current_user.id,
        name=f"{plan.name} - 购物清单",
    )

    db.add(shopping_list)
    db.flush()

    # 添加购物清单项
    for key, data in ingredient_summary.items():
        if data["quantity"] > 0:
            list_item = ShoppingListItem(
                shopping_list_id=shopping_list.id,
                ingredient_name=data["name"],
                quantity=round(data["quantity"], 2),
                unit=data["unit"],
            )
            db.add(list_item)

    db.commit()
    db.refresh(shopping_list)

    return shopping_list
