# 个人菜谱管理与饮食计划API服务

基于 FastAPI + PostgreSQL 开发的个人菜谱管理与饮食计划系统。

## 功能特性

- **用户认证**：邮箱/用户名注册登录，支持"记住我"功能延长登录有效期
- **菜谱管理**：创建、编辑、删除菜谱，支持多步骤图文混排，标签分类（素食/低卡/快手菜等）
- **饮食计划**：按周安排每日三餐（早餐/午餐/晚餐/加餐）
- **购物清单**：根据饮食计划自动汇总所需食材生成购物清单
- **营养估算**：根据食材库计算菜谱的卡路里、蛋白质、脂肪、碳水化合物含量

## 技术栈

- **后端框架**: FastAPI
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **数据校验**: Pydantic 2.0
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt (passlib)

## 项目结构

```
test32/
├── app/
│   ├── __init__.py
│   ├── config.py              # 配置文件
│   ├── database.py            # 数据库连接
│   ├── core/
│   │   ├── __init__.py
│   │   └── security.py        # 安全认证模块
│   ├── models/                # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── tag.py
│   │   ├── ingredient.py
│   │   ├── meal_plan.py
│   │   └── shopping.py
│   ├── schemas/               # Pydantic数据校验模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── tag.py
│   │   ├── ingredient.py
│   │   ├── meal_plan.py
│   │   ├── shopping.py
│   │   └── common.py
│   └── api/                   # API路由
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           ├── auth.py        # 认证接口
│           ├── users.py       # 用户接口
│           ├── recipes.py     # 菜谱接口
│           ├── tags.py        # 标签接口
│           ├── ingredients.py # 食材接口
│           ├── meal_plans.py  # 饮食计划接口
│           ├── shopping.py    # 购物清单接口
│           └── nutrition.py   # 营养估算接口
├── sql/
│   └── init.sql               # 数据库初始化脚本
├── main.py                    # 应用入口
├── requirements.txt           # 依赖列表
├── .env.example               # 环境变量示例
└── .gitignore                 # Git忽略规则
```

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

### 2. 激活虚拟环境

**Windows PowerShell**:
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows CMD**:
```cmd
.\.venv\Scripts\activate.bat
```

**Linux/Mac**:
```bash
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/recipe_management

# JWT配置（请修改为随机密钥）
SECRET_KEY=your-secret-key-change-in-production

# Token有效期
ACCESS_TOKEN_EXPIRE_MINUTES=30
REMEMBER_ME_TOKEN_EXPIRE_DAYS=7
```

### 5. 初始化数据库

1. 创建PostgreSQL数据库：
```sql
CREATE DATABASE recipe_management;
```

2. 执行初始化脚本：
```bash
psql -U postgres -d recipe_management -f sql/init.sql
```

### 6. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口列表

### 认证模块 `/api/v1/auth`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/register` | 用户注册 |
| POST | `/login` | 用户登录（支持记住我） |
| POST | `/refresh` | 刷新Token |
| GET | `/me` | 获取当前用户信息 |

### 用户模块 `/api/v1/users`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/me` | 获取个人信息 |
| PUT | `/me` | 更新个人信息 |
| DELETE | `/me` | 删除账号 |

### 菜谱模块 `/api/v1/recipes`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/` | 创建菜谱 |
| GET | `/` | 获取菜谱列表 |
| GET | `/{recipe_id}` | 获取菜谱详情 |
| PUT | `/{recipe_id}` | 更新菜谱 |
| DELETE | `/{recipe_id}` | 删除菜谱 |
| POST | `/{recipe_id}/steps` | 添加步骤 |
| PUT | `/steps/{step_id}` | 更新步骤 |
| DELETE | `/steps/{step_id}` | 删除步骤 |
| POST | `/{recipe_id}/ingredients` | 添加食材 |
| PUT | `/ingredients/{ingredient_id}` | 更新食材 |
| DELETE | `/ingredients/{ingredient_id}` | 删除食材 |

### 标签模块 `/api/v1/tags`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/` | 创建标签 |
| GET | `/` | 获取标签列表 |
| GET | `/{tag_id}` | 获取标签详情 |
| PUT | `/{tag_id}` | 更新标签 |
| DELETE | `/{tag_id}` | 删除标签 |

### 食材模块 `/api/v1/ingredients`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/` | 创建食材 |
| GET | `/` | 获取食材列表 |
| GET | `/{ingredient_id}` | 获取食材详情 |
| PUT | `/{ingredient_id}` | 更新食材 |
| DELETE | `/{ingredient_id}` | 删除食材 |

### 饮食计划模块 `/api/v1/meal-plans`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/` | 创建饮食计划 |
| GET | `/` | 获取计划列表 |
| GET | `/{plan_id}` | 获取计划详情 |
| PUT | `/{plan_id}` | 更新计划 |
| DELETE | `/{plan_id}` | 删除计划 |
| POST | `/{plan_id}/items` | 添加餐项 |
| PUT | `/items/{item_id}` | 更新餐项 |
| DELETE | `/items/{item_id}` | 删除餐项 |
| POST | `/{plan_id}/generate-shopping-list` | 生成购物清单 |

### 购物清单模块 `/api/v1/shopping`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 获取清单列表 |
| GET | `/{list_id}` | 获取清单详情 |
| PUT | `/{list_id}` | 更新清单 |
| DELETE | `/{list_id}` | 删除清单 |
| PUT | `/items/{item_id}` | 更新清单项 |
| DELETE | `/items/{item_id}` | 删除清单项 |
| POST | `/items/{item_id}/toggle-purchased` | 切换购买状态 |

### 营养估算模块 `/api/v1/nutrition`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/recipe/{recipe_id}` | 计算菜谱营养 |
| GET | `/meal-plan/{plan_id}` | 计算计划营养 |
| POST | `/custom` | 计算自定义营养 |

## 默认标签

系统初始化时会创建以下默认标签：

- 素食 - 不含肉类、鱼类等动物产品
- 低卡 - 低热量、适合减脂期
- 快手菜 - 30分钟内可以完成
- 高蛋白 - 富含蛋白质，适合增肌期
- 家常菜 - 常见的家常菜
- 低脂 - 低脂肪含量
- 低碳水 - 低碳水化合物
- 早餐 - 适合作为早餐
- 午餐 - 适合作为午餐
- 晚餐 - 适合作为晚餐

## 使用示例

### 1. 用户注册

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "confirm_password": "password123",
    "full_name": "测试用户"
  }'
```

### 2. 用户登录

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "user@example.com",
    "password": "password123",
    "remember_me": true
  }'
```

### 3. 创建菜谱

```bash
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "番茄炒蛋",
    "description": "简单快手的家常菜",
    "cooking_time": 15,
    "servings": 2,
    "difficulty": "easy",
    "steps": [
      {
        "step_number": 1,
        "description": "番茄切块，鸡蛋打散",
        "image_url": ""
      },
      {
        "step_number": 2,
        "description": "热锅下油，倒入蛋液炒至凝固盛出",
        "image_url": ""
      }
    ],
    "ingredients": [
      {
        "ingredient_name": "番茄",
        "quantity": 2,
        "unit": "个"
      },
      {
        "ingredient_name": "鸡蛋",
        "quantity": 3,
        "unit": "个"
      }
    ],
    "tag_ids": []
  }'
```

## 许可证

MIT License
