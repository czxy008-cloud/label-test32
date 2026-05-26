"""
个人菜谱管理与饮食计划API服务
FastAPI主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api import api_router
from app.models import *  # noqa: F401, F403 - 导入所有模型以确保表被注册


# =============================================================================
# 应用生命周期管理
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    - 启动时创建数据库表
    - 关闭时清理资源
    """
    # 启动时创建所有表
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时可以添加清理逻辑


# =============================================================================
# 创建FastAPI应用
# =============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    个人菜谱管理与饮食计划API服务
    
    ## 功能特性
    
    - 用户认证：注册、登录、记住我功能
    - 菜谱管理：创建、编辑、多步骤图文混排、标签分类
    - 饮食计划：按周安排每日三餐
    - 购物清单：自动汇总食材生成购物清单
    - 营养估算：根据食材库计算卡路里与蛋白质含量
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# =============================================================================
# CORS配置
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# 路由注册
# =============================================================================

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


# =============================================================================
# 基础路由
# =============================================================================

@app.get("/", tags=["基础"])
async def root():
    """
    API根路径
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["基础"])
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


# =============================================================================
# 异常处理
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误",
            "error": str(exc) if settings.DEBUG else "请联系管理员"
        }
    )
