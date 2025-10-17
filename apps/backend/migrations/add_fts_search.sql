-- ========================================
-- SQLite FTS5 全文搜索优化迁移脚本
-- 用于优化画廊搜索性能（适用于 1000+ 作品）
-- ========================================

-- 1. 创建 FTS5 虚拟表（简化版，不使用外部内容表）
CREATE VIRTUAL TABLE IF NOT EXISTS creations_fts USING fts5(
    creation_id,  -- 作品ID（用于关联）
    prompt,       -- 索引提示词
    tags          -- 索引标签
);

-- 2. 触发器：同步 INSERT 操作
CREATE TRIGGER IF NOT EXISTS creations_fts_insert 
AFTER INSERT ON creations 
BEGIN
    INSERT INTO creations_fts(creation_id, prompt, tags)
    VALUES (new.id, new.prompt, COALESCE(new.tags, ''));
END;

-- 3. 触发器：同步 UPDATE 操作
CREATE TRIGGER IF NOT EXISTS creations_fts_update 
AFTER UPDATE ON creations 
BEGIN
    DELETE FROM creations_fts WHERE creation_id = old.id;
    INSERT INTO creations_fts(creation_id, prompt, tags)
    VALUES (new.id, new.prompt, COALESCE(new.tags, ''));
END;

-- 4. 触发器：同步 DELETE 操作
CREATE TRIGGER IF NOT EXISTS creations_fts_delete 
AFTER DELETE ON creations 
BEGIN
    DELETE FROM creations_fts WHERE creation_id = old.id;
END;

-- 5. 初始化：导入现有数据到 FTS5 表
INSERT INTO creations_fts(creation_id, prompt, tags)
SELECT id, prompt, COALESCE(tags, '') 
FROM creations;

-- 6. 优化 FTS5 索引（可选，提升查询性能）
INSERT INTO creations_fts(creations_fts) VALUES('optimize');

