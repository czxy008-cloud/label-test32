# 数据库迁移脚本

本目录包含数据库迁移脚本，用于管理数据库结构的变更。

## 迁移脚本列表

### 001_add_bookmarks_table.sql
**功能：** 添加用户收藏菜谱功能所需的数据库表结构

**执行方式：**
```bash
# PostgreSQL
psql -U your_username -d your_database -f sql/migrations/001_add_bookmarks_table.sql
```

**注意：** 如果使用 SQLAlchemy 的 `Base.metadata.create_all()`，则会自动创建 bookmarks 表，无需手动执行迁移脚本。

## 迁移脚本内容说明

### 001_add_bookmarks_table.sql
创建以下数据库对象：

1. **bookmarks 表** - 存储用户与菜谱的收藏关联关系
   - `id`: UUID 主键
   - `user_id`: 用户ID（外键，级联删除）
   - `recipe_id`: 菜谱ID（外键，级联删除）
   - `created_at`: 收藏时间

2. **复合唯一约束 `uq_user_recipe_bookmark`**
   - 防止同一用户重复收藏同一菜谱

3. **索引优化**
   - `idx_bookmarks_user_id`: 用户收藏查询优化
   - `idx_bookmarks_recipe_id`: 菜谱收藏数查询优化
   - `idx_bookmarks_user_created`: 按收藏时间排序查询优化

## 级联删除说明

- 当用户被删除时，该用户的所有收藏记录自动删除
- 当菜谱被删除时，所有关联该菜谱的收藏记录自动删除
