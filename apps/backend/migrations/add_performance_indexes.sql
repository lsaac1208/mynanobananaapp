-- ==========================================================================
-- 性能优化索引
-- 为关键查询添加数据库索引以提升查询性能
-- ==========================================================================

-- ========================================
-- 作品表 (creations) 索引优化
-- ========================================

-- 用户作品查询 - 最常用的查询模式
-- 使用场景: 画廊页面按时间倒序查询用户作品
CREATE INDEX IF NOT EXISTS idx_creations_user_created 
  ON creations(user_id, created_at DESC);

-- 分类查询
-- 使用场景: 按分类筛选作品
CREATE INDEX IF NOT EXISTS idx_creations_category 
  ON creations(category) 
  WHERE category IS NOT NULL;

-- 收藏查询 - 部分索引
-- 使用场景: 查询用户收藏的作品
CREATE INDEX IF NOT EXISTS idx_creations_favorite 
  ON creations(user_id, is_favorite) 
  WHERE is_favorite = 1;

-- 标签查询（如果需要按标签搜索）
-- 使用场景: 标签筛选
CREATE INDEX IF NOT EXISTS idx_creations_tags 
  ON creations(tags) 
  WHERE tags IS NOT NULL AND tags != '';

-- 综合查询索引 - 支持复杂筛选
-- 使用场景: 同时按用户、分类、时间查询
CREATE INDEX IF NOT EXISTS idx_creations_composite 
  ON creations(user_id, category, created_at DESC);

-- ========================================
-- 性能指标表 (performance_metrics) 索引优化
-- ========================================

-- 时间序列查询
-- 使用场景: 查询最近的性能数据
CREATE INDEX IF NOT EXISTS idx_performance_timestamp 
  ON performance_metrics(timestamp DESC);

-- 用户性能分析
-- 使用场景: 分析特定用户的操作性能
CREATE INDEX IF NOT EXISTS idx_performance_user_operation 
  ON performance_metrics(user_id, operation_type, timestamp DESC);

-- 成功率分析
-- 使用场景: 查询失败的请求
CREATE INDEX IF NOT EXISTS idx_performance_success 
  ON performance_metrics(success, timestamp DESC);

-- 操作类型分析
-- 使用场景: 按操作类型统计性能
CREATE INDEX IF NOT EXISTS idx_performance_operation 
  ON performance_metrics(operation_type, timestamp DESC);

-- ========================================
-- 用户会话表 (user_sessions) 索引优化
-- ========================================

-- 活跃会话查询
-- 使用场景: 查询当前活跃的用户会话
CREATE INDEX IF NOT EXISTS idx_sessions_user_active 
  ON user_sessions(user_id, is_active, login_time DESC);

-- 会话时间范围查询
-- 使用场景: 统计时间段内的登录
CREATE INDEX IF NOT EXISTS idx_sessions_time_range 
  ON user_sessions(login_time DESC, logout_time DESC);

-- ========================================
-- 用户行为表 (user_behavior) 索引优化
-- ========================================

-- 用户行为时间序列
-- 使用场景: 查询用户的操作历史
CREATE INDEX IF NOT EXISTS idx_behavior_user_timestamp 
  ON user_behavior(user_id, timestamp DESC);

-- 行为类型分析
-- 使用场景: 统计各种行为的发生频率
CREATE INDEX IF NOT EXISTS idx_behavior_action 
  ON user_behavior(action_type, timestamp DESC);

-- ========================================
-- 每日统计表 (daily_stats) 索引优化
-- ========================================

-- 日期查询
-- 使用场景: 按日期查询统计数据
CREATE INDEX IF NOT EXISTS idx_daily_stats_date 
  ON daily_stats(date DESC);

-- 用户每日统计
-- 使用场景: 查询特定用户的每日数据
CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date 
  ON daily_stats(user_id, date DESC);

-- ========================================
-- JWT黑名单表 (jwt_blacklist) 索引优化
-- ========================================

-- JTI查询
-- 使用场景: 检查token是否被撤销（高频查询）
CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_jti 
  ON jwt_blacklist(jti);

-- 清理过期记录
-- 使用场景: 定期清理旧的黑名单记录
CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_created 
  ON jwt_blacklist(created_at DESC);

-- ========================================
-- 用户表 (users) 索引优化
-- ========================================

-- 邮箱查询（已有UNIQUE约束，自动创建索引）
-- 登录时间查询
CREATE INDEX IF NOT EXISTS idx_users_last_login 
  ON users(last_login_at DESC) 
  WHERE last_login_at IS NOT NULL;

-- 活跃用户查询
CREATE INDEX IF NOT EXISTS idx_users_active 
  ON users(is_active, created_at DESC);

-- ========================================
-- 智能推荐表 (smart_recommendations) 索引优化
-- ========================================

-- 用户推荐查询
CREATE INDEX IF NOT EXISTS idx_recommendations_user 
  ON smart_recommendations(user_id, created_at DESC);

-- 推荐类型查询
CREATE INDEX IF NOT EXISTS idx_recommendations_type 
  ON smart_recommendations(recommendation_type, created_at DESC);

-- ========================================
-- 系统设置表 (system_settings) 索引优化
-- ========================================

-- key查询（可能已有UNIQUE约束）
CREATE INDEX IF NOT EXISTS idx_system_settings_key 
  ON system_settings(key);

-- 更新时间查询
CREATE INDEX IF NOT EXISTS idx_system_settings_updated 
  ON system_settings(updated_at DESC);

-- ==========================================================================
-- 索引维护建议
-- ==========================================================================

-- 定期分析索引使用情况:
-- PRAGMA index_list('table_name');
-- PRAGMA index_info('index_name');

-- 定期重建索引以提升性能:
-- REINDEX index_name;
-- REINDEX table_name;

-- 分析查询计划:
-- EXPLAIN QUERY PLAN 
-- SELECT * FROM creations WHERE user_id = ? ORDER BY created_at DESC LIMIT 20;

-- ==========================================================================
-- 性能测试查询示例
-- ==========================================================================

-- 测试1: 用户作品查询（应使用 idx_creations_user_created）
-- EXPLAIN QUERY PLAN 
-- SELECT * FROM creations 
-- WHERE user_id = 1 
-- ORDER BY created_at DESC 
-- LIMIT 20;

-- 测试2: 收藏作品查询（应使用 idx_creations_favorite）
-- EXPLAIN QUERY PLAN 
-- SELECT * FROM creations 
-- WHERE user_id = 1 AND is_favorite = 1 
-- ORDER BY created_at DESC;

-- 测试3: 分类查询（应使用 idx_creations_category）
-- EXPLAIN QUERY PLAN 
-- SELECT * FROM creations 
-- WHERE category = 'landscape' 
-- ORDER BY created_at DESC;

-- 测试4: 性能指标查询（应使用 idx_performance_user_operation）
-- EXPLAIN QUERY PLAN 
-- SELECT * FROM performance_metrics 
-- WHERE user_id = 1 AND operation_type = 'text_to_image' 
-- ORDER BY timestamp DESC 
-- LIMIT 10;

-- ==========================================================================
-- 执行说明
-- ==========================================================================

-- 方式1: 通过SQLite命令行
-- sqlite3 instance/database.db < apps/backend/migrations/add_performance_indexes.sql

-- 方式2: 通过Python脚本
-- python apps/backend/migrations/apply_indexes.py

-- ==========================================================================
-- 预期性能提升
-- ==========================================================================

-- 画廊查询:    无索引 ~200ms  →  有索引 ~10-30ms  (85-95% 提升)
-- 统计查询:    无索引 ~150ms  →  有索引 ~5-15ms   (90-97% 提升)
-- 性能指标:    无索引 ~100ms  →  有索引 ~5-10ms   (90-95% 提升)
-- JWT检查:     无索引 ~10ms   →  有索引 ~1-2ms    (80-90% 提升)

-- ==========================================================================
-- 注意事项
-- ==========================================================================

-- 1. 索引会增加写入时间（约5-10%），但大幅提升读取速度
-- 2. 定期清理不再使用的索引
-- 3. 监控数据库文件大小（索引会增加存储空间）
-- 4. 对于小表（<1000行）索引收益不明显
-- 5. 使用 ANALYZE 命令更新查询优化器统计信息

-- 更新统计信息
ANALYZE;

