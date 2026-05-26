-- =============================================================================
-- 个人菜谱管理与饮食计划系统 数据库初始化脚本
-- 数据库: PostgreSQL
-- 版本: 1.0
-- 日期: 2024
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 创建数据库（如果不存在）
-- -----------------------------------------------------------------------------
-- CREATE DATABASE recipe_management
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'en_US.utf8'
--     LC_CTYPE = 'en_US.utf8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1;

-- 连接到数据库后执行以下建表语句

-- -----------------------------------------------------------------------------
-- 启用UUID扩展
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. 用户表 (users)
-- 存储系统用户信息，支持邮箱登录
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 用户唯一标识
    email           VARCHAR(255) NOT NULL UNIQUE,                         -- 邮箱地址（登录用）
    username        VARCHAR(50) NOT NULL UNIQUE,                          -- 用户名
    password_hash   VARCHAR(255) NOT NULL,                                -- 密码哈希（bcrypt加密）
    full_name       VARCHAR(100),                                         -- 真实姓名
    avatar_url      VARCHAR(500),                                         -- 头像图片URL
    is_active       BOOLEAN DEFAULT TRUE,                                 -- 账号是否激活
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 更新时间
);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- -----------------------------------------------------------------------------
-- 用户表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE users IS '用户信息表';
COMMENT ON COLUMN users.id IS '用户唯一标识（UUID）';
COMMENT ON COLUMN users.email IS '邮箱地址，用于登录和接收通知';
COMMENT ON COLUMN users.username IS '用户名，显示用';
COMMENT ON COLUMN users.password_hash IS '密码哈希值，使用bcrypt算法加密存储';
COMMENT ON COLUMN users.full_name IS '用户真实姓名';
COMMENT ON COLUMN users.avatar_url IS '用户头像图片URL地址';
COMMENT ON COLUMN users.is_active IS '账号状态：true=活跃，false=已禁用';
COMMENT ON COLUMN users.created_at IS '账号创建时间';
COMMENT ON COLUMN users.updated_at IS '账号信息最后更新时间';

-- =============================================================================
-- 2. 食材营养信息表 (ingredients)
-- 存储食材库及其基础营养信息，用于营养估算
-- =============================================================================
CREATE TABLE IF NOT EXISTS ingredients (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 食材唯一标识
    name            VARCHAR(100) NOT NULL UNIQUE,                         -- 食材名称
    category        VARCHAR(50) NOT NULL,                                 -- 食材分类（蔬菜/肉类/主食等）
    unit            VARCHAR(20) NOT NULL DEFAULT 'g',                     -- 计量单位（g/ml/个/片）
    calories        DECIMAL(10, 2) DEFAULT 0,                             -- 每单位热量（卡路里）
    protein         DECIMAL(10, 2) DEFAULT 0,                             -- 每单位蛋白质含量（克）
    fat             DECIMAL(10, 2) DEFAULT 0,                             -- 每单位脂肪含量（克）
    carbohydrates   DECIMAL(10, 2) DEFAULT 0,                             -- 每单位碳水化合物含量（克）
    description     TEXT,                                                  -- 食材描述
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 更新时间
);

-- 食材表索引
CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_category ON ingredients(category);

-- -----------------------------------------------------------------------------
-- 食材表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE ingredients IS '食材营养信息表';
COMMENT ON COLUMN ingredients.id IS '食材唯一标识（UUID）';
COMMENT ON COLUMN ingredients.name IS '食材名称';
COMMENT ON COLUMN ingredients.category IS '食材分类：蔬菜/水果/肉类/主食/调料/其他';
COMMENT ON COLUMN ingredients.unit IS '计量单位：g/ml/个/片/勺等';
COMMENT ON COLUMN ingredients.calories IS '每单位食材的热量（卡路里）';
COMMENT ON COLUMN ingredients.protein IS '每单位食材的蛋白质含量（克）';
COMMENT ON COLUMN ingredients.fat IS '每单位食材的脂肪含量（克）';
COMMENT ON COLUMN ingredients.carbohydrates IS '每单位食材的碳水化合物含量（克）';
COMMENT ON COLUMN ingredients.description IS '食材详细描述';
COMMENT ON COLUMN ingredients.created_at IS '食材信息创建时间';
COMMENT ON COLUMN ingredients.updated_at IS '食材信息最后更新时间';

-- =============================================================================
-- 3. 菜谱表 (recipes)
-- 存储用户创建的菜谱基本信息
-- =============================================================================
CREATE TABLE IF NOT EXISTS recipes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 菜谱唯一标识
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- 所属用户ID
    title           VARCHAR(200) NOT NULL,                                 -- 菜谱标题
    description     TEXT,                                                  -- 菜谱描述
    cover_image     VARCHAR(500),                                          -- 封面图片URL
    cooking_time    INTEGER NOT NULL DEFAULT 0,                            -- 烹饪时间（分钟）
    servings        INTEGER NOT NULL DEFAULT 1,                            -- 份量（人份）
    difficulty      VARCHAR(20) DEFAULT 'easy',                            -- 难度等级：easy/medium/hard
    is_public       BOOLEAN DEFAULT FALSE,                                 -- 是否公开
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 更新时间
);

-- 菜谱表索引
CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_title ON recipes(title);
CREATE INDEX IF NOT EXISTS idx_recipes_is_public ON recipes(is_public);

-- -----------------------------------------------------------------------------
-- 菜谱表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE recipes IS '菜谱基本信息表';
COMMENT ON COLUMN recipes.id IS '菜谱唯一标识（UUID）';
COMMENT ON COLUMN recipes.user_id IS '菜谱创建者用户ID，关联users表';
COMMENT ON COLUMN recipes.title IS '菜谱标题名称';
COMMENT ON COLUMN recipes.description IS '菜谱详细描述';
COMMENT ON COLUMN recipes.cover_image IS '菜谱封面图片URL';
COMMENT ON COLUMN recipes.cooking_time IS '预估烹饪时间（分钟）';
COMMENT ON COLUMN recipes.servings IS '菜谱份量，可供几人食用';
COMMENT ON COLUMN recipes.difficulty IS '烹饪难度：easy=简单, medium=中等, hard=困难';
COMMENT ON COLUMN recipes.is_public IS '是否公开给其他用户查看';
COMMENT ON COLUMN recipes.created_at IS '菜谱创建时间';
COMMENT ON COLUMN recipes.updated_at IS '菜谱最后更新时间';

-- =============================================================================
-- 4. 菜谱步骤表 (recipe_steps)
-- 存储菜谱的烹饪步骤，支持多步骤图文混排
-- =============================================================================
CREATE TABLE IF NOT EXISTS recipe_steps (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 步骤唯一标识
    recipe_id       UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE, -- 所属菜谱ID
    step_number     INTEGER NOT NULL,                                      -- 步骤序号
    description     TEXT NOT NULL,                                         -- 步骤描述文字
    image_url       VARCHAR(500),                                          -- 步骤配图URL
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 更新时间
    UNIQUE(recipe_id, step_number)                                         -- 保证同一菜谱内步骤序号唯一
);

-- 步骤表索引
CREATE INDEX IF NOT EXISTS idx_recipe_steps_recipe_id ON recipe_steps(recipe_id);

-- -----------------------------------------------------------------------------
-- 菜谱步骤表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE recipe_steps IS '菜谱烹饪步骤表';
COMMENT ON COLUMN recipe_steps.id IS '步骤唯一标识（UUID）';
COMMENT ON COLUMN recipe_steps.recipe_id IS '所属菜谱ID，关联recipes表';
COMMENT ON COLUMN recipe_steps.step_number IS '步骤序号，从1开始';
COMMENT ON COLUMN recipe_steps.description IS '步骤操作描述文字';
COMMENT ON COLUMN recipe_steps.image_url IS '步骤配图URL，支持图文混排';
COMMENT ON COLUMN recipe_steps.created_at IS '步骤创建时间';
COMMENT ON COLUMN recipe_steps.updated_at IS '步骤最后更新时间';

-- =============================================================================
-- 5. 菜谱食材关联表 (recipe_ingredients)
-- 存储菜谱所需的食材及用量
-- =============================================================================
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 记录唯一标识
    recipe_id       UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE, -- 所属菜谱ID
    ingredient_id   UUID REFERENCES ingredients(id) ON DELETE SET NULL,   -- 关联食材库ID（可选）
    ingredient_name VARCHAR(100) NOT NULL,                                 -- 食材名称（冗余存储方便展示）
    quantity        DECIMAL(10, 2) NOT NULL,                               -- 用量数值
    unit            VARCHAR(20) NOT NULL,                                  -- 计量单位
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 更新时间
);

-- 菜谱食材表索引
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id);

-- -----------------------------------------------------------------------------
-- 菜谱食材表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE recipe_ingredients IS '菜谱食材关联表';
COMMENT ON COLUMN recipe_ingredients.id IS '记录唯一标识（UUID）';
COMMENT ON COLUMN recipe_ingredients.recipe_id IS '所属菜谱ID，关联recipes表';
COMMENT ON COLUMN recipe_ingredients.ingredient_id IS '关联食材库ID，用于营养计算，可为空';
COMMENT ON COLUMN recipe_ingredients.ingredient_name IS '食材名称，冗余存储便于快速展示';
COMMENT ON COLUMN recipe_ingredients.quantity IS '食材用量数值';
COMMENT ON COLUMN recipe_ingredients.unit IS '食材计量单位';
COMMENT ON COLUMN recipe_ingredients.created_at IS '记录创建时间';
COMMENT ON COLUMN recipe_ingredients.updated_at IS '记录最后更新时间';

-- =============================================================================
-- 6. 标签表 (tags)
-- 存储菜谱标签分类，如素食/低卡/快手菜等
-- =============================================================================
CREATE TABLE IF NOT EXISTS tags (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 标签唯一标识
    name            VARCHAR(50) NOT NULL UNIQUE,                           -- 标签名称
    description     TEXT,                                                  -- 标签描述
    color           VARCHAR(20) DEFAULT '#1890ff',                         -- 标签颜色（十六进制）
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 创建时间
);

-- 标签表注释
COMMENT ON TABLE tags IS '菜谱标签分类表';
COMMENT ON COLUMN tags.id IS '标签唯一标识（UUID）';
COMMENT ON COLUMN tags.name IS '标签名称，如：素食、低卡、快手菜、高蛋白等';
COMMENT ON COLUMN tags.description IS '标签详细描述';
COMMENT ON COLUMN tags.color IS '标签显示颜色（十六进制色值）';
COMMENT ON COLUMN tags.created_at IS '标签创建时间';

-- =============================================================================
-- 7. 菜谱-标签关联表 (recipe_tags)
-- 菜谱与标签的多对多关联表
-- =============================================================================
CREATE TABLE IF NOT EXISTS recipe_tags (
    recipe_id       UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    tag_id          UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY(recipe_id, tag_id)                                        -- 复合主键，防止重复关联
);

-- 菜谱标签关联表注释
COMMENT ON TABLE recipe_tags IS '菜谱-标签多对多关联表';
COMMENT ON COLUMN recipe_tags.recipe_id IS '菜谱ID，关联recipes表';
COMMENT ON COLUMN recipe_tags.tag_id IS '标签ID，关联tags表';
COMMENT ON COLUMN recipe_tags.created_at IS '关联创建时间';

-- =============================================================================
-- 8. 饮食计划表 (meal_plans)
-- 存储用户制定的饮食计划（按周管理）
-- =============================================================================
CREATE TABLE IF NOT EXISTS meal_plans (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 计划唯一标识
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- 所属用户ID
    name            VARCHAR(100) NOT NULL,                                 -- 计划名称
    start_date      DATE NOT NULL,                                         -- 计划开始日期
    end_date        DATE NOT NULL,                                         -- 计划结束日期
    notes           TEXT,                                                  -- 计划备注
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 更新时间
);

-- 饮食计划表索引
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_plans_date_range ON meal_plans(start_date, end_date);

-- -----------------------------------------------------------------------------
-- 饮食计划表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE meal_plans IS '饮食计划表（按周管理）';
COMMENT ON COLUMN meal_plans.id IS '饮食计划唯一标识（UUID）';
COMMENT ON COLUMN meal_plans.user_id IS '计划所属用户ID，关联users表';
COMMENT ON COLUMN meal_plans.name IS '计划名称，如：减脂计划、家常菜计划';
COMMENT ON COLUMN meal_plans.start_date IS '计划开始日期';
COMMENT ON COLUMN meal_plans.end_date IS '计划结束日期';
COMMENT ON COLUMN meal_plans.notes IS '计划备注说明';
COMMENT ON COLUMN meal_plans.created_at IS '计划创建时间';
COMMENT ON COLUMN meal_plans.updated_at IS '计划最后更新时间';

-- =============================================================================
-- 9. 饮食计划详情表 (meal_plan_items)
-- 存储每日三餐与菜谱的具体关联
-- =============================================================================
CREATE TABLE IF NOT EXISTS meal_plan_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 详情唯一标识
    meal_plan_id    UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE, -- 所属计划ID
    recipe_id       UUID REFERENCES recipes(id) ON DELETE SET NULL,       -- 关联菜谱ID（可选）
    date            DATE NOT NULL,                                         -- 计划日期
    meal_type       VARCHAR(20) NOT NULL,                                  -- 餐类型：breakfast/lunch/dinner/snack
    custom_recipe_name VARCHAR(200),                                       -- 自定义菜名（当不关联菜谱时使用）
    notes           TEXT,                                                  -- 备注
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 更新时间
);

-- 饮食计划详情表索引
CREATE INDEX IF NOT EXISTS idx_meal_plan_items_plan_id ON meal_plan_items(meal_plan_id);
CREATE INDEX IF NOT EXISTS idx_meal_plan_items_date ON meal_plan_items(date);
CREATE INDEX IF NOT EXISTS idx_meal_plan_items_meal_type ON meal_plan_items(meal_type);

-- -----------------------------------------------------------------------------
-- 饮食计划详情表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE meal_plan_items IS '饮食计划详情表（每日三餐安排）';
COMMENT ON COLUMN meal_plan_items.id IS '详情唯一标识（UUID）';
COMMENT ON COLUMN meal_plan_items.meal_plan_id IS '所属饮食计划ID，关联meal_plans表';
COMMENT ON COLUMN meal_plan_items.recipe_id IS '关联的菜谱ID，关联recipes表';
COMMENT ON COLUMN meal_plan_items.date IS '计划执行的日期';
COMMENT ON COLUMN meal_plan_items.meal_type IS '餐次类型：breakfast=早餐, lunch=午餐, dinner=晚餐, snack=加餐';
COMMENT ON COLUMN meal_plan_items.custom_recipe_name IS '自定义菜名，当不选择已有菜谱时使用';
COMMENT ON COLUMN meal_plan_items.notes IS '本条计划的备注说明';
COMMENT ON COLUMN meal_plan_items.created_at IS '记录创建时间';
COMMENT ON COLUMN meal_plan_items.updated_at IS '记录最后更新时间';

-- =============================================================================
-- 10. 购物清单表 (shopping_lists)
-- 存储根据饮食计划自动生成的购物清单
-- =============================================================================
CREATE TABLE IF NOT EXISTS shopping_lists (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 清单唯一标识
    meal_plan_id    UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE, -- 关联饮食计划ID
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- 所属用户ID
    name            VARCHAR(100) NOT NULL,                                 -- 清单名称
    is_completed    BOOLEAN DEFAULT FALSE,                                 -- 是否已完成采购
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()                -- 更新时间
);

-- 购物清单表索引
CREATE INDEX IF NOT EXISTS idx_shopping_lists_plan_id ON shopping_lists(meal_plan_id);
CREATE INDEX IF NOT EXISTS idx_shopping_lists_user_id ON shopping_lists(user_id);

-- -----------------------------------------------------------------------------
-- 购物清单表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE shopping_lists IS '购物清单表';
COMMENT ON COLUMN shopping_lists.id IS '购物清单唯一标识（UUID）';
COMMENT ON COLUMN shopping_lists.meal_plan_id IS '关联的饮食计划ID，关联meal_plans表';
COMMENT ON COLUMN shopping_lists.user_id IS '清单所属用户ID，关联users表';
COMMENT ON COLUMN shopping_lists.name IS '清单名称，如：第1周购物清单';
COMMENT ON COLUMN shopping_lists.is_completed IS '是否已完成采购：true=已完成';
COMMENT ON COLUMN shopping_lists.created_at IS '清单创建时间';
COMMENT ON COLUMN shopping_lists.updated_at IS '清单最后更新时间';

-- =============================================================================
-- 11. 购物清单详情表 (shopping_list_items)
-- 存储购物清单中的具体食材项
-- =============================================================================
CREATE TABLE IF NOT EXISTS shopping_list_items (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),       -- 详情唯一标识
    shopping_list_id    UUID NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE, -- 所属清单ID
    ingredient_name     VARCHAR(100) NOT NULL,                             -- 食材名称
    quantity            DECIMAL(10, 2) NOT NULL,                           -- 总需求量
    unit                VARCHAR(20) NOT NULL,                              -- 计量单位
    is_purchased        BOOLEAN DEFAULT FALSE,                             -- 是否已购买
    notes               TEXT,                                              -- 备注
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),           -- 创建时间
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()            -- 更新时间
);

-- 购物清单详情表索引
CREATE INDEX IF NOT EXISTS idx_shopping_list_items_list_id ON shopping_list_items(shopping_list_id);
CREATE INDEX IF NOT EXISTS idx_shopping_list_items_purchased ON shopping_list_items(is_purchased);

-- -----------------------------------------------------------------------------
-- 购物清单详情表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE shopping_list_items IS '购物清单详情表';
COMMENT ON COLUMN shopping_list_items.id IS '详情唯一标识（UUID）';
COMMENT ON COLUMN shopping_list_items.shopping_list_id IS '所属购物清单ID，关联shopping_lists表';
COMMENT ON COLUMN shopping_list_items.ingredient_name IS '食材名称';
COMMENT ON COLUMN shopping_list_items.quantity IS '需要采购的总数量（系统自动汇总计算）';
COMMENT ON COLUMN shopping_list_items.unit IS '计量单位';
COMMENT ON COLUMN shopping_list_items.is_purchased IS '是否已购买：true=已购买';
COMMENT ON COLUMN shopping_list_items.notes IS '备注说明';
COMMENT ON COLUMN shopping_list_items.created_at IS '记录创建时间';
COMMENT ON COLUMN shopping_list_items.updated_at IS '记录最后更新时间';

-- =============================================================================
-- 初始化数据：插入默认标签
-- =============================================================================
INSERT INTO tags (name, description, color) VALUES
    ('素食', '不含肉类、鱼类等动物产品的菜谱', '#52c41a'),
    ('低卡', '低热量、适合减脂期的菜谱', '#faad14'),
    ('快手菜', '30分钟内可以完成的简易菜谱', '#1890ff'),
    ('高蛋白', '富含蛋白质，适合增肌期的菜谱', '#eb2f96'),
    ('家常菜', '常见的家常菜谱', '#722ed1'),
    ('低脂', '低脂肪含量的菜谱', '#13c2c2'),
    ('低碳水', '低碳水化合物，适合生酮饮食', '#f5222d'),
    ('早餐', '适合作为早餐的菜谱', '#fa541c'),
    ('午餐', '适合作为午餐的菜谱', '#2f54eb'),
    ('晚餐', '适合作为晚餐的菜谱', '#722ed1')
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- 初始化数据：插入示例食材营养信息
-- =============================================================================
INSERT INTO ingredients (name, category, unit, calories, protein, fat, carbohydrates) VALUES
    ('鸡胸肉', '肉类', 'g', 1.65, 0.31, 0.04, 0),
    ('鸡蛋', '蛋类', '个', 78, 6.5, 5.0, 0.6),
    ('米饭', '主食', 'g', 1.3, 0.03, 0.003, 0.28),
    ('西兰花', '蔬菜', 'g', 0.34, 0.028, 0.004, 0.07),
    ('胡萝卜', '蔬菜', 'g', 0.41, 0.009, 0.002, 0.096),
    ('西红柿', '蔬菜', 'g', 0.18, 0.009, 0.002, 0.039),
    ('牛肉', '肉类', 'g', 2.50, 0.26, 0.15, 0),
    ('鱼肉', '肉类', 'g', 2.06, 0.20, 0.13, 0),
    ('豆腐', '豆制品', 'g', 0.76, 0.08, 0.048, 0.019),
    ('牛奶', '乳制品', 'ml', 0.42, 0.034, 0.01, 0.05),
    ('燕麦', '主食', 'g', 3.89, 0.169, 0.07, 0.66),
    ('苹果', '水果', '个', 95, 0.47, 0.31, 25),
    ('香蕉', '水果', '根', 105, 1.29, 0.39, 27),
    ('橄榄油', '调料', 'ml', 8.0, 0, 0.92, 0),
    ('盐', '调料', 'g', 0, 0, 0, 0),
    ('酱油', '调料', 'ml', 0.53, 0.081, 0.004, 0.049),
    ('面条', '主食', 'g', 1.38, 0.05, 0.007, 0.27),
    ('土豆', '蔬菜', 'g', 0.77, 0.02, 0.001, 0.17),
    ('洋葱', '蔬菜', 'g', 0.4, 0.011, 0.001, 0.09),
    ('大蒜', '调料', '瓣', 4.5, 0.19, 0.01, 1.0)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- 创建更新时间触发器函数
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =============================================================================
-- 为各表创建更新时间触发器
-- =============================================================================
-- users表触发器
DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- recipes表触发器
DROP TRIGGER IF EXISTS trg_recipes_updated_at ON recipes;
CREATE TRIGGER trg_recipes_updated_at
    BEFORE UPDATE ON recipes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- recipe_steps表触发器
DROP TRIGGER IF EXISTS trg_recipe_steps_updated_at ON recipe_steps;
CREATE TRIGGER trg_recipe_steps_updated_at
    BEFORE UPDATE ON recipe_steps
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ingredients表触发器
DROP TRIGGER IF EXISTS trg_ingredients_updated_at ON ingredients;
CREATE TRIGGER trg_ingredients_updated_at
    BEFORE UPDATE ON ingredients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- meal_plans表触发器
DROP TRIGGER IF EXISTS trg_meal_plans_updated_at ON meal_plans;
CREATE TRIGGER trg_meal_plans_updated_at
    BEFORE UPDATE ON meal_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- meal_plan_items表触发器
DROP TRIGGER IF EXISTS trg_meal_plan_items_updated_at ON meal_plan_items;
CREATE TRIGGER trg_meal_plan_items_updated_at
    BEFORE UPDATE ON meal_plan_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- shopping_lists表触发器
DROP TRIGGER IF EXISTS trg_shopping_lists_updated_at ON shopping_lists;
CREATE TRIGGER trg_shopping_lists_updated_at
    BEFORE UPDATE ON shopping_lists
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- shopping_list_items表触发器
DROP TRIGGER IF EXISTS trg_shopping_list_items_updated_at ON shopping_list_items;
CREATE TRIGGER trg_shopping_list_items_updated_at
    BEFORE UPDATE ON shopping_list_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
