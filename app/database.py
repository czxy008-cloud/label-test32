"""
数据库连接模块
管理SQLAlchemy引擎和会话
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖注入函数
    确保请求结束后会话被正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
