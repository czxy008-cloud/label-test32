"""
应用配置模块
集中管理所有配置项，支持环境变量覆盖
"""

import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置类"""

    # 基础配置
    APP_NAME: str = "个人菜谱管理与饮食计划API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/recipe_management"
    )

    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REMEMBER_ME_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REMEMBER_ME_TOKEN_EXPIRE_DAYS", "7"))

    # 文件上传配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100


settings = Settings()
