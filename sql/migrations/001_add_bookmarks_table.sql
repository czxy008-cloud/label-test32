-- =============================================================================
-- 迁移脚本: 001_add_bookmarks_table
-- 描述: 添加用户收藏菜谱功能所需的数据库表结构
-- 版本: 1.0
-- 日期: 2024
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. 创建收藏表 (bookmarks)
-- 存储用户收藏的菜谱关联关系
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookmarks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),           -- 收藏记录唯一标识
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,  -- 用户ID
    recipe_id       UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,-- 菜谱ID
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),               -- 创建时间
    -- 复合唯一索引：防止用户重复收藏同一菜谱
    CONSTRAINT uq_user_recipe_bookmark UNIQUE(user_id, recipe_id)
);

-- -----------------------------------------------------------------------------
-- 2. 创建索引以优化查询性能
-- -----------------------------------------------------------------------------
-- 用户收藏查询索引
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks(user_id);
-- 菜谱收藏数查询索引
CREATE INDEX IF NOT EXISTS idx_bookmarks_recipe_id ON bookmarks(recipe_id);
-- 按收藏时间排序索引
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_created ON bookmarks(user_id, created_at DESC);

-- -----------------------------------------------------------------------------
-- 表注释
-- -----------------------------------------------------------------------------
COMMENT ON TABLE bookmarks IS '用户收藏菜谱关联表';
COMMENT ON COLUMN bookmarks.id IS '收藏记录唯一标识（UUID）';
COMMENT ON COLUMN bookmarks.user_id IS '用户ID，关联users表，级联删除';
COMMENT ON COLUMN bookmarks.recipe_id IS '菜谱ID，关联recipes表，级联删除';
COMMENT ON COLUMN bookmarks.created_at IS '收藏时间';

-- =============================================================================
-- 迁移完成说明
-- =============================================================================
-- 此迁移脚本添加了以下内容：
-- 1. bookmarks表：存储用户与菜谱的收藏关联关系
-- 2. 复合唯一约束uq_user_recipe_bookmark：防止用户重复收藏同一菜谱
-- 3. 多个索引优化查询性能
--
-- 级联删除说明：
-- - 当用户被删除时，该用户的所有收藏记录自动删除
-- - 当菜谱被删除时，所有关联该菜谱的收藏记录自动删除
-- =============================================================================
