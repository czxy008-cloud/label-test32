"""
API路由模块
统一管理所有API路由
"""

from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.recipes import router as recipes_router
from app.api.routes.tags import router as tags_router
from app.api.routes.ingredients import router as ingredients_router
from app.api.routes.meal_plans import router as meal_plans_router
from app.api.routes.shopping import router as shopping_router
from app.api.routes.nutrition import router as nutrition_router
from app.api.routes.users import router as users_router

# 创建API v1路由器
api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户"])
api_router.include_router(recipes_router, prefix="/recipes", tags=["菜谱"])
api_router.include_router(tags_router, prefix="/tags", tags=["标签"])
api_router.include_router(ingredients_router, prefix="/ingredients", tags=["食材"])
api_router.include_router(meal_plans_router, prefix="/meal-plans", tags=["饮食计划"])
api_router.include_router(shopping_router, prefix="/shopping", tags=["购物清单"])
api_router.include_router(nutrition_router, prefix="/nutrition", tags=["营养"])
