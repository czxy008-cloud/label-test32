"""
食材营养信息模型
定义食材库表结构
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Ingredient(Base):
    """食材营养信息模型"""

    __tablename__ = "ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False, default="g")
    calories = Column(Numeric(10, 2), default=0)
    protein = Column(Numeric(10, 2), default=0)
    fat = Column(Numeric(10, 2), default=0)
    carbohydrates = Column(Numeric(10, 2), default=0)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    recipes = relationship("RecipeIngredient", back_populates="ingredient")

    def __repr__(self):
        return f"<Ingredient {self.name}>"
