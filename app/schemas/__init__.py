"""
Pydantic Schemas模块
定义所有请求/响应数据校验模型
"""

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserWithToken,
    TokenResponse,
    LoginRequest,
)
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
from app.schemas.tag import (
    TagCreate,
    TagResponse,
    TagWithRecipes,
)
from app.schemas.ingredient import (
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse,
    NutritionInfo,
)
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
    ShoppingListUpdate,
    ShoppingListResponse,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListItemResponse,
    ShoppingListWithItems,
)
from app.schemas.bookmark import (
    BookmarkCreate,
    BookmarkResponse,
    BookmarkStatusResponse,
    BookmarkRecipeResponse,
)
from app.schemas.common import (
    PaginatedResponse,
    MessageResponse,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserWithToken",
    "TokenResponse",
    "LoginRequest",
    # Recipe schemas
    "RecipeCreate",
    "RecipeUpdate",
    "RecipeResponse",
    "RecipeListResponse",
    "RecipeStepCreate",
    "RecipeStepUpdate",
    "RecipeStepResponse",
    "RecipeIngredientCreate",
    "RecipeIngredientUpdate",
    "RecipeIngredientResponse",
    "RecipeWithBookmarkResponse",
    # Tag schemas
    "TagCreate",
    "TagResponse",
    "TagWithRecipes",
    # Ingredient schemas
    "IngredientCreate",
    "IngredientUpdate",
    "IngredientResponse",
    "NutritionInfo",
    # Meal Plan schemas
    "MealPlanCreate",
    "MealPlanUpdate",
    "MealPlanResponse",
    "MealPlanItemCreate",
    "MealPlanItemUpdate",
    "MealPlanItemResponse",
    "MealPlanWithDetails",
    # Shopping schemas
    "ShoppingListCreate",
    "ShoppingListUpdate",
    "ShoppingListResponse",
    "ShoppingListItemCreate",
    "ShoppingListItemUpdate",
    "ShoppingListItemResponse",
    "ShoppingListWithItems",
    # Bookmark schemas
    "BookmarkCreate",
    "BookmarkResponse",
    "BookmarkStatusResponse",
    "BookmarkRecipeResponse",
    # Common schemas
    "PaginatedResponse",
    "MessageResponse",
]
