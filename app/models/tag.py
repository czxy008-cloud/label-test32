"""
标签模型
定义菜谱标签及关联表结构
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Tag(Base):
    """标签模型"""

    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    color = Column(String(20), default="#1890ff")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # 关联关系
    recipe_tags = relationship("RecipeTag", back_populates="tag", cascade="all, delete-orphan")
    recipes = relationship("Recipe", secondary="recipe_tags", back_populates="tags", viewonly=True)

    def __repr__(self):
        return f"<Tag {self.name}>"


class RecipeTag(Base):
    """菜谱-标签关联模型"""

    __tablename__ = "recipe_tags"

    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # 关联关系
    recipe = relationship("Recipe", back_populates="recipe_tags")
    tag = relationship("Tag", back_populates="recipe_tags")

    def __repr__(self):
        return f"<RecipeTag recipe:{self.recipe_id} tag:{self.tag_id}>"
