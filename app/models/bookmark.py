"""
收藏模型
定义用户收藏菜谱的关联表结构
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Bookmark(Base):
    """用户收藏菜谱模型"""

    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'recipe_id', name='uq_user_recipe_bookmark'),
    )

    user = relationship("User", back_populates="bookmarks")
    recipe = relationship("Recipe", back_populates="bookmarks")

    def __repr__(self):
        return f"<Bookmark user:{self.user_id} recipe:{self.recipe_id}>"
