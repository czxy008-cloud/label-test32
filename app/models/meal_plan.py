"""
饮食计划模型
定义饮食计划及详情表结构
"""

from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class MealPlan(Base):
    """饮食计划模型"""

    __tablename__ = "meal_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="meal_plans")
    items = relationship("MealPlanItem", back_populates="meal_plan", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="meal_plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MealPlan {self.name}>"


class MealPlanItem(Base):
    """饮食计划详情模型"""

    __tablename__ = "meal_plan_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meal_plan_id = Column(UUID(as_uuid=True), ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, nullable=False)
    meal_type = Column(String(20), nullable=False)  # breakfast/lunch/dinner/snack
    custom_recipe_name = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    meal_plan = relationship("MealPlan", back_populates="items")
    recipe = relationship("Recipe")

    def __repr__(self):
        return f"<MealPlanItem {self.date}:{self.meal_type}>"
