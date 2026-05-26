"""
购物清单路由
处理购物清单的查询、更新等操作
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.shopping import ShoppingList, ShoppingListItem
from app.schemas.shopping import (
    ShoppingListUpdate,
    ShoppingListResponse,
    ShoppingListWithItems,
    ShoppingListItemUpdate,
    ShoppingListItemResponse,
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


@router.get("", response_model=List[ShoppingListResponse])
async def list_shopping_lists(
    is_completed: Optional[bool] = Query(None, description="完成状态筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的购物清单列表

    - 支持按完成状态筛选
    """
    query = db.query(ShoppingList).filter(ShoppingList.user_id == current_user.id)

    if is_completed is not None:
        query = query.filter(ShoppingList.is_completed == is_completed)

    lists = query.order_by(ShoppingList.created_at.desc()).all()

    return lists


@router.get("/{list_id}", response_model=ShoppingListWithItems)
async def get_shopping_list(
    list_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取购物清单详情

    - 包含所有清单项
    """
    list_uuid = _parse_uuid(list_id, "清单ID")
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == list_uuid,
        ShoppingList.user_id == current_user.id
    ).first()

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物清单不存在"
        )

    return shopping_list


@router.put("/{list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    list_id: str,
    list_data: ShoppingListUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新购物清单信息

    - 可更新名称和完成状态
    """
    list_uuid = _parse_uuid(list_id, "清单ID")
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == list_uuid,
        ShoppingList.user_id == current_user.id
    ).first()

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物清单不存在"
        )

    if list_data.name is not None:
        shopping_list.name = list_data.name
    if list_data.is_completed is not None:
        shopping_list.is_completed = list_data.is_completed

    db.commit()
    db.refresh(shopping_list)

    return shopping_list


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除购物清单
    """
    list_uuid = _parse_uuid(list_id, "清单ID")
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == list_uuid,
        ShoppingList.user_id == current_user.id
    ).first()

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物清单不存在"
        )

    db.delete(shopping_list)
    db.commit()

    return None


# =============================================================================
# 购物清单项管理
# =============================================================================

@router.put("/items/{item_id}", response_model=ShoppingListItemResponse)
async def update_shopping_list_item(
    item_id: str,
    item_data: ShoppingListItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新购物清单项

    - 可标记为已购买
    """
    item_uuid = _parse_uuid(item_id, "清单项ID")
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == item_uuid
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物清单项不存在"
        )

    # 检查权限
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == item.shopping_list_id,
        ShoppingList.user_id == current_user.id
    ).first()

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此购物清单"
        )

    if item_data.ingredient_name is not None:
        item.ingredient_name = item_data.ingredient_name
    if item_data.quantity is not None:
        item.quantity = item_data.quantity
    if item_data.unit is not None:
        item.unit = item_data.unit
    if item_data.is_purchased is not None:
        item.is_purchased = item_data.is_purchased
    if item_data.notes is not None:
        item.notes = item_data.notes

    db.commit()
    db.refresh(item)

    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除购物清单项
    """
    item_uuid = _parse_uuid(item_id, "清单项ID")
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == item_uuid
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物清单项不存在"
        )

    # 检查权限
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == item.shopping_list_id,
        ShoppingList.user_id == current_user.id
    ).first()

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此购物清单"
        )

    db.delete(item)
    db.commit()

    return None


@router.post("/items/{item_id}/toggle-purchased", response_model=ShoppingListItemResponse)
async def toggle_item_purchased(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    切换购物清单项的购买状态
    """
    item_uuid = _parse_uuid(item_id, "清单项ID")
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == item_uuid
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物清单项不存在"
        )

    # 检查权限
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == item.shopping_list_id,
        ShoppingList.user_id == current_user.id
    ).first()

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此购物清单"
        )

    item.is_purchased = not item.is_purchased

    db.commit()
    db.refresh(item)

    return item
