"""
营养估算路由
根据食材库计算菜谱的大致卡路里与蛋白质含量等营养信息
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe, RecipeIngredient
from app.models.ingredient import Ingredient
from app.models.meal_plan import MealPlan, MealPlanItem
from app.schemas.ingredient import NutritionInfo
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


@router.get("/recipe/{recipe_id}", response_model=NutritionInfo)
async def calculate_recipe_nutrition(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    计算菜谱的营养信息

    - 根据食材库匹配营养数据
    - 计算总热量、蛋白质、脂肪、碳水化合物
    - 同时返回每份的营养信息
    """
    recipe_uuid = _parse_uuid(recipe_id, "菜谱ID")
    recipe = db.query(Recipe).filter(Recipe.id == recipe_uuid).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜谱不存在"
        )

    # 检查权限
    if recipe.user_id != current_user.id and not recipe.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此菜谱"
        )

    # 获取菜谱食材
    recipe_ingredients = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_uuid
    ).all()

    # 计算营养信息
    total_calories = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbohydrates = 0.0
    details = []

    for ri in recipe_ingredients:
        nutrition_data = {
            "ingredient_name": ri.ingredient_name,
            "quantity": float(ri.quantity),
            "unit": ri.unit,
            "calories": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
        }

        # 尝试从食材库获取营养信息
        if ri.ingredient_id:
            ingredient = db.query(Ingredient).filter(
                Ingredient.id == ri.ingredient_id
            ).first()

            if ingredient:
                # 根据数量计算营养值
                multiplier = float(ri.quantity)
                nutrition_data["calories"] = round(float(ingredient.calories) * multiplier, 2)
                nutrition_data["protein"] = round(float(ingredient.protein) * multiplier, 2)
                nutrition_data["fat"] = round(float(ingredient.fat) * multiplier, 2)
                nutrition_data["carbohydrates"] = round(float(ingredient.carbohydrates) * multiplier, 2)

        # 如果没有匹配到食材库，尝试按名称匹配
        if nutrition_data["calories"] == 0:
            ingredient = db.query(Ingredient).filter(
                Ingredient.name == ri.ingredient_name
            ).first()

            if ingredient:
                multiplier = float(ri.quantity)
                nutrition_data["calories"] = round(float(ingredient.calories) * multiplier, 2)
                nutrition_data["protein"] = round(float(ingredient.protein) * multiplier, 2)
                nutrition_data["fat"] = round(float(ingredient.fat) * multiplier, 2)
                nutrition_data["carbohydrates"] = round(float(ingredient.carbohydrates) * multiplier, 2)

        total_calories += nutrition_data["calories"]
        total_protein += nutrition_data["protein"]
        total_fat += nutrition_data["fat"]
        total_carbohydrates += nutrition_data["carbohydrates"]
        details.append(nutrition_data)

    servings = recipe.servings if recipe.servings > 0 else 1

    return NutritionInfo(
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_fat=round(total_fat, 2),
        total_carbohydrates=round(total_carbohydrates, 2),
        per_serving_calories=round(total_calories / servings, 2),
        per_serving_protein=round(total_protein / servings, 2),
        per_serving_fat=round(total_fat / servings, 2),
        per_serving_carbohydrates=round(total_carbohydrates / servings, 2),
        servings=servings,
        details=details,
    )


@router.get("/meal-plan/{plan_id}", response_model=NutritionInfo)
async def calculate_meal_plan_nutrition(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    计算饮食计划的总营养信息

    - 汇总计划内所有菜谱的营养信息
    - 显示每日平均营养摄入
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

    # 计算营养信息
    total_calories = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbohydrates = 0.0

    for item in plan_items:
        if item.recipe_id:
            # 获取菜谱食材
            recipe_ingredients = db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == item.recipe_id
            ).all()

            for ri in recipe_ingredients:
                # 尝试从食材库获取营养信息
                ingredient = None
                if ri.ingredient_id:
                    ingredient = db.query(Ingredient).filter(
                        Ingredient.id == ri.ingredient_id
                    ).first()

                if not ingredient:
                    ingredient = db.query(Ingredient).filter(
                        Ingredient.name == ri.ingredient_name
                    ).first()

                if ingredient:
                    multiplier = float(ri.quantity)
                    total_calories += float(ingredient.calories) * multiplier
                    total_protein += float(ingredient.protein) * multiplier
                    total_fat += float(ingredient.fat) * multiplier
                    total_carbohydrates += float(ingredient.carbohydrates) * multiplier

    # 计算天数
    days = (plan.end_date - plan.start_date).days + 1
    if days <= 0:
        days = 1

    return NutritionInfo(
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_fat=round(total_fat, 2),
        total_carbohydrates=round(total_carbohydrates, 2),
        per_serving_calories=round(total_calories / days, 2),
        per_serving_protein=round(total_protein / days, 2),
        per_serving_fat=round(total_fat / days, 2),
        per_serving_carbohydrates=round(total_carbohydrates / days, 2),
        servings=days,
        details=[],
    )


@router.post("/custom", response_model=NutritionInfo)
async def calculate_custom_nutrition(
    ingredients: list[dict],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    计算自定义食材组合的营养信息

    - 传入食材名称和数量列表
    - 返回总营养信息
    """
    total_calories = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbohydrates = 0.0
    details = []

    for item in ingredients:
        ingredient_name = item.get("name")
        quantity = float(item.get("quantity", 1))

        nutrition_data = {
            "ingredient_name": ingredient_name,
            "quantity": quantity,
            "unit": item.get("unit", "g"),
            "calories": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
        }

        # 查找食材库
        ingredient = db.query(Ingredient).filter(
            Ingredient.name == ingredient_name
        ).first()

        if ingredient:
            multiplier = quantity
            nutrition_data["calories"] = round(float(ingredient.calories) * multiplier, 2)
            nutrition_data["protein"] = round(float(ingredient.protein) * multiplier, 2)
            nutrition_data["fat"] = round(float(ingredient.fat) * multiplier, 2)
            nutrition_data["carbohydrates"] = round(float(ingredient.carbohydrates) * multiplier, 2)

        total_calories += nutrition_data["calories"]
        total_protein += nutrition_data["protein"]
        total_fat += nutrition_data["fat"]
        total_carbohydrates += nutrition_data["carbohydrates"]
        details.append(nutrition_data)

    return NutritionInfo(
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_fat=round(total_fat, 2),
        total_carbohydrates=round(total_carbohydrates, 2),
        per_serving_calories=round(total_calories, 2),
        per_serving_protein=round(total_protein, 2),
        per_serving_fat=round(total_fat, 2),
        per_serving_carbohydrates=round(total_carbohydrates, 2),
        servings=1,
        details=details,
    )
