"""
简化的SQLite数据库管理
"""
import sqlite3
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from flask import g, current_app
from werkzeug.security import generate_password_hash, check_password_hash


def get_db_path():
    """获取数据库文件路径"""
    return os.path.join(current_app.instance_path, 'database.db')


def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        db_path = get_db_path()
        # 确保instance目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row  # 使结果可以像字典一样访问

        # 启用外键约束（安全加固）
        g.db.execute('PRAGMA foreign_keys = ON')

        # 启用WAL模式提升并发性能
        g.db.execute('PRAGMA journal_mode = WAL')
    return g.db


def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """初始化数据库表"""
    db = get_db()

    # 创建用户表
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            credits INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login_at DATETIME,
            login_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until DATETIME
        )
    ''')

    # 创建作品表
    db.execute('''
        CREATE TABLE IF NOT EXISTS creations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            image_url TEXT NOT NULL,
            model_used TEXT NOT NULL,
            size TEXT NOT NULL,
            generation_time REAL,
            is_favorite BOOLEAN NOT NULL DEFAULT 0,
            tags TEXT DEFAULT '',
            category TEXT DEFAULT 'general',
            visibility TEXT DEFAULT 'private',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 创建JWT黑名单表
    db.execute('''
        CREATE TABLE IF NOT EXISTS jwt_blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jti TEXT NOT NULL UNIQUE,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # === 性能监控与用户行为分析表 (Phase 1) ===

    # 用户会话表 - 跟踪用户活动会话
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            logout_time DATETIME,
            ip_address TEXT,
            user_agent TEXT,
            duration_seconds INTEGER,
            pages_visited INTEGER DEFAULT 0,
            generations_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 性能指标表 - 记录系统和AI生成性能数据
    db.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            operation_type TEXT NOT NULL, -- 'text_to_image', 'image_to_image', 'api_call'
            model_used TEXT,
            prompt_length INTEGER,
            image_size TEXT,
            generation_time REAL, -- AI生成时间(秒)
            api_response_time REAL, -- API响应时间(秒)
            queue_wait_time REAL, -- 队列等待时间(秒)
            success BOOLEAN NOT NULL DEFAULT 1,
            error_type TEXT, -- 错误类型：'timeout', 'api_error', 'validation_error'
            error_message TEXT, -- 错误详情
            server_load REAL, -- 服务器负载 (0-1)
            memory_usage_mb INTEGER, -- 内存使用量
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')

    # 用户行为分析表 - 记录用户操作和偏好
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_behaviors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT,
            action_type TEXT NOT NULL, -- 'login', 'generate', 'view_gallery', 'download', 'favorite'
            target_id INTEGER, -- 关联的创作ID（如果适用）
            parameters TEXT, -- JSON格式参数：模型选择、尺寸偏好等
            page_url TEXT, -- 操作页面
            referrer TEXT, -- 来源页面
            device_type TEXT, -- 'desktop', 'mobile', 'tablet'
            browser TEXT, -- 浏览器类型
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 每日统计汇总表 - 用于快速查询和报表
    db.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            total_users INTEGER DEFAULT 0,
            active_users INTEGER DEFAULT 0,
            new_registrations INTEGER DEFAULT 0,
            total_generations INTEGER DEFAULT 0,
            successful_generations INTEGER DEFAULT 0,
            avg_generation_time REAL DEFAULT 0,
            total_credits_consumed INTEGER DEFAULT 0,
            peak_concurrent_users INTEGER DEFAULT 0,
            error_rate REAL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # === Phase 2: 智能推荐系统表 ===

    # 用户偏好配置表 - 存储用户的个人偏好设置
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            preferred_model TEXT DEFAULT 'nano-banana', -- 偏好的AI模型
            preferred_size TEXT DEFAULT '1x1', -- 偏好的图片尺寸
            preferred_quality TEXT DEFAULT 'standard', -- 偏好的图片质量
            generation_style TEXT, -- 生成风格偏好: 'realistic', 'artistic', 'cartoon', 'abstract'
            prompt_language TEXT DEFAULT 'chinese', -- 提示词语言偏好
            auto_enhance_prompts BOOLEAN DEFAULT 0, -- 是否自动优化提示词
            save_generation_history BOOLEAN DEFAULT 1, -- 是否保存生成历史
            enable_smart_suggestions BOOLEAN DEFAULT 1, -- 是否启用智能建议
            notification_preferences TEXT, -- JSON格式通知偏好
            privacy_level TEXT DEFAULT 'private', -- 隐私级别
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id)
        )
    ''')

    # 智能推荐记录表 - 记录系统为用户生成的推荐
    db.execute('''
        CREATE TABLE IF NOT EXISTS smart_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recommendation_type TEXT NOT NULL, -- 'model', 'size', 'prompt_enhancement', 'style', 'similar_creations'
            original_input TEXT, -- 用户的原始输入
            recommended_value TEXT NOT NULL, -- 推荐的值或内容
            recommendation_reason TEXT, -- 推荐理由说明
            confidence_score REAL DEFAULT 0.5, -- 推荐置信度 (0-1)
            context_data TEXT, -- JSON格式上下文数据
            user_action TEXT, -- 用户对推荐的操作: 'accepted', 'rejected', 'ignored', 'modified'
            effectiveness_score REAL, -- 推荐效果评分 (0-1)
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            acted_at DATETIME, -- 用户采取行动的时间
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 提示词优化建议表 - 存储提示词优化的建议和规则
    db.execute('''
        CREATE TABLE IF NOT EXISTS prompt_optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT NOT NULL,
            optimization_type TEXT NOT NULL, -- 'enhancement', 'translation', 'style_adjustment', 'quality_improvement'
            improvement_description TEXT, -- 改进说明
            keywords_added TEXT, -- 添加的关键词
            keywords_removed TEXT, -- 移除的关键词
            style_tags TEXT, -- 风格标签
            quality_metrics TEXT, -- JSON格式质量指标
            success_rate REAL DEFAULT 0, -- 优化成功率
            usage_count INTEGER DEFAULT 0, -- 使用次数
            avg_generation_time REAL, -- 平均生成时间
            avg_user_satisfaction REAL, -- 平均用户满意度
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 相似作品关联表 - 建立作品间的相似性关系
    db.execute('''
        CREATE TABLE IF NOT EXISTS creation_similarities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creation_id_1 INTEGER NOT NULL,
            creation_id_2 INTEGER NOT NULL,
            similarity_score REAL NOT NULL, -- 相似度评分 (0-1)
            similarity_type TEXT NOT NULL, -- 'visual', 'prompt', 'style', 'keyword'
            shared_features TEXT, -- JSON格式共同特征
            calculated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creation_id_1) REFERENCES creations (id) ON DELETE CASCADE,
            FOREIGN KEY (creation_id_2) REFERENCES creations (id) ON DELETE CASCADE,
            UNIQUE(creation_id_1, creation_id_2, similarity_type)
        )
    ''')

    # 推荐效果统计表 - 跟踪推荐系统的整体效果
    db.execute('''
        CREATE TABLE IF NOT EXISTS recommendation_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            recommendation_type TEXT NOT NULL,
            total_recommendations INTEGER DEFAULT 0,
            accepted_recommendations INTEGER DEFAULT 0,
            rejected_recommendations INTEGER DEFAULT 0,
            acceptance_rate REAL DEFAULT 0, -- 接受率
            avg_confidence_score REAL DEFAULT 0, -- 平均置信度
            avg_effectiveness_score REAL DEFAULT 0, -- 平均效果评分
            user_satisfaction_improvement REAL DEFAULT 0, -- 用户满意度改善
            generation_time_improvement REAL DEFAULT 0, -- 生成时间改善
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, recommendation_type)
        )
    ''')

    # === 系统配置表 (System Settings) ===
    db.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT,
            description TEXT,
            is_encrypted BOOLEAN DEFAULT 0,
            updated_by INTEGER,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (updated_by) REFERENCES users (id)
        )
    ''')

    # 检查并添加新的列（数据库迁移）
    try:
        # 尝试添加新列
        db.execute('ALTER TABLE creations ADD COLUMN is_favorite BOOLEAN NOT NULL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # 列已存在

    try:
        db.execute('ALTER TABLE creations ADD COLUMN tags TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass

    try:
        db.execute('ALTER TABLE creations ADD COLUMN category TEXT DEFAULT "general"')
    except sqlite3.OperationalError:
        pass

    try:
        db.execute('ALTER TABLE creations ADD COLUMN visibility TEXT DEFAULT "private"')
    except sqlite3.OperationalError:
        pass

    try:
        db.execute('ALTER TABLE creations ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP')
    except sqlite3.OperationalError:
        pass

    db.commit()


class User:
    """用户模型"""

    @staticmethod
    def create(email: str, password: str) -> Optional[int]:
        """创建新用户"""
        db = get_db()
        # 使用 werkzeug 的 pbkdf2:sha256 哈希算法（更安全）
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            cursor = db.execute(
                'INSERT INTO users (email, password_hash, credits) VALUES (?, ?, ?)',
                (email, password_hash, 5)  # 默认给5次生成机会
            )
            db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # 邮箱已存在

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        return dict(user) if user else None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        return dict(user) if user else None

    @staticmethod
    def verify_password(user: Dict[str, Any], password: str) -> bool:
        """验证密码（支持新旧格式兼容）"""
        stored_hash = user['password_hash']
        
        # 检查是否是新格式（pbkdf2:sha256 哈希以 'pbkdf2:sha256:' 开头）
        if stored_hash.startswith('pbkdf2:sha256:'):
            # 使用 werkzeug 验证新格式密码
            is_valid = check_password_hash(stored_hash, password)
            return is_valid
        else:
            # 兼容旧格式（SHA256）
            old_hash = hashlib.sha256(password.encode()).hexdigest()
            is_valid = stored_hash == old_hash
            
            # 如果验证成功，自动升级到新格式
            if is_valid:
                User.upgrade_password_hash(user['id'], password)
            
            return is_valid
    
    @staticmethod
    def upgrade_password_hash(user_id: int, password: str):
        """将用户密码哈希升级到新格式"""
        db = get_db()
        new_hash = generate_password_hash(password, method='pbkdf2:sha256')
        db.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (new_hash, user_id)
        )
        db.commit()

    @staticmethod
    def update_login_info(user_id: int, success: bool = True):
        """更新登录信息"""
        db = get_db()
        now = datetime.now().isoformat()

        if success:
            db.execute(
                'UPDATE users SET last_login_at = ?, login_attempts = 0, locked_until = NULL WHERE id = ?',
                (now, user_id)
            )
        else:
            # 增加失败次数
            db.execute(
                'UPDATE users SET login_attempts = login_attempts + 1 WHERE id = ?',
                (user_id,)
            )

            # 检查是否需要锁定账户
            user = User.get_by_id(user_id)
            if user and user['login_attempts'] >= 5:
                # 锁定30分钟
                from datetime import timedelta
                lock_until = (datetime.now() + timedelta(minutes=30)).isoformat()
                db.execute(
                    'UPDATE users SET locked_until = ? WHERE id = ?',
                    (lock_until, user_id)
                )

        db.commit()

    @staticmethod
    def is_locked(user: Dict[str, Any]) -> bool:
        """检查用户是否被锁定"""
        if not user.get('locked_until'):
            return False

        lock_time = datetime.fromisoformat(user['locked_until'])
        return datetime.now() < lock_time

    @staticmethod
    def consume_credits(user_id: int, amount: int = 1) -> bool:
        """消费用户次数"""
        db = get_db()

        # 检查当前次数
        user = User.get_by_id(user_id)
        if not user or user['credits'] < amount:
            return False

        # 扣除次数
        db.execute(
            'UPDATE users SET credits = credits - ? WHERE id = ?',
            (amount, user_id)
        )
        db.commit()
        return True

    @staticmethod
    def refund_credits(user_id: int, amount: int = 1):
        """退还用户次数"""
        db = get_db()
        db.execute(
            'UPDATE users SET credits = credits + ? WHERE id = ?',
            (amount, user_id)
        )
        db.commit()

    @staticmethod
    def add_credits(user_id: int, amount: int):
        """添加用户次数（管理员功能）"""
        db = get_db()
        db.execute(
            'UPDATE users SET credits = credits + ? WHERE id = ?',
            (amount, user_id)
        )
        db.commit()

    @staticmethod
    def delete_user_cascade(user_id: int, admin_id: int, reason: str = '') -> Dict[str, Any]:
        """
        级联删除用户及相关数据（管理员功能）

        Args:
            user_id: 要删除的用户ID
            admin_id: 执行删除的管理员ID
            reason: 删除原因

        Returns:
            包含删除结果和影响范围的字典
        """
        db = get_db()

        try:
            # 1. 防止自我删除 (关键安全检查)
            if user_id == admin_id:
                raise ValueError(f'Cannot delete self - admin user {admin_id} attempted to delete themselves')

            # 2. 验证用户存在
            user = db.execute('SELECT id, email FROM users WHERE id = ?', (user_id,)).fetchone()
            if not user:
                raise ValueError(f'User {user_id} not found')

            user_email = user['email']

            # 3. 统计影响范围（删除前）
            impact = {
                'creations_orphaned': db.execute(
                    'SELECT COUNT(*) as count FROM creations WHERE user_id = ?', (user_id,)
                ).fetchone()['count'],
                'sessions_deleted': db.execute(
                    'SELECT COUNT(*) as count FROM user_sessions WHERE user_id = ?', (user_id,)
                ).fetchone()['count'],
                'behaviors_deleted': db.execute(
                    'SELECT COUNT(*) as count FROM user_behaviors WHERE user_id = ?', (user_id,)
                ).fetchone()['count'],
                'preferences_deleted': db.execute(
                    'SELECT COUNT(*) as count FROM user_preferences WHERE user_id = ?', (user_id,)
                ).fetchone()['count'],
                'recommendations_deleted': db.execute(
                    'SELECT COUNT(*) as count FROM smart_recommendations WHERE user_id = ?', (user_id,)
                ).fetchone()['count'],
                'performance_metrics_deleted': db.execute(
                    'SELECT COUNT(*) as count FROM performance_metrics WHERE user_id = ?', (user_id,)
                ).fetchone()['count']
            }

            # 4. 执行级联删除
            # 软删除：将作品标记为孤儿（保留内容）
            db.execute('''
                UPDATE creations
                SET user_id = NULL, is_orphaned = 1
                WHERE user_id = ?
            ''', (user_id,))

            # 硬删除：用户特定数据
            db.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))
            db.execute('DELETE FROM user_behaviors WHERE user_id = ?', (user_id,))
            db.execute('DELETE FROM user_preferences WHERE user_id = ?', (user_id,))
            db.execute('DELETE FROM smart_recommendations WHERE user_id = ?', (user_id,))
            db.execute('DELETE FROM performance_metrics WHERE user_id = ?', (user_id,))

            # 5. 记录审计日志
            data_summary = f"Orphaned {impact['creations_orphaned']} creations, " \
                          f"deleted {sum(impact.values()) - impact['creations_orphaned']} records"

            db.execute('''
                INSERT INTO user_deletions
                (deleted_user_id, deleted_user_email, admin_user_id, reason,
                 creations_orphaned, data_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, user_email, admin_id, reason or 'Admin action',
                  impact['creations_orphaned'], data_summary))

            # 6. 删除用户记录
            db.execute('DELETE FROM users WHERE id = ?', (user_id,))

            db.commit()

            return {
                'message': 'User deleted successfully',
                'deleted_user': {
                    'id': user_id,
                    'email': user_email,
                    'deleted_at': datetime.now().isoformat() + 'Z'
                },
                'impact': impact
            }

        except Exception as e:
            db.rollback()
            raise


class Creation:
    """作品模型"""

    @staticmethod
    def create(user_id: int, prompt: str, image_url: str, model_used: str,
               size: str, generation_time: float = None, tags: str = '',
               category: str = 'general', visibility: str = 'private') -> int:
        """创建新作品记录"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO creations
               (user_id, prompt, image_url, model_used, size, generation_time, tags, category, visibility)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, prompt, image_url, model_used, size, generation_time, tags, category, visibility)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_user(user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取用户的作品列表"""
        db = get_db()
        creations = db.execute(
            '''SELECT * FROM creations
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?''',
            (user_id, limit, offset)
        ).fetchall()
        return [dict(creation) for creation in creations]

    @staticmethod
    def get_by_id(creation_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取作品"""
        db = get_db()
        creation = db.execute(
            'SELECT * FROM creations WHERE id = ?', (creation_id,)
        ).fetchone()
        return dict(creation) if creation else None

    @staticmethod
    def delete(creation_id: int, user_id: int) -> bool:
        """删除作品（仅限作品所有者）"""
        db = get_db()
        result = db.execute(
            'DELETE FROM creations WHERE id = ? AND user_id = ?',
            (creation_id, user_id)
        )
        db.commit()
        return result.rowcount > 0

    @staticmethod
    def get_by_user_with_filters(user_id: int, limit: int = 20, offset: int = 0,
                                category: str = None, tags: str = None,
                                search: str = None, is_favorite: bool = None) -> List[Dict[str, Any]]:
        """获取用户的作品列表（带筛选功能）"""
        db = get_db()

        # 构建查询条件
        conditions = ['user_id = ?']
        params = [user_id]

        if category and category != 'all':
            conditions.append('category = ?')
            params.append(category)

        if tags:
            conditions.append('tags LIKE ?')
            params.append(f'%{tags}%')

        if search:
            # 优化：使用 FTS5 全文搜索（如果表存在）
            try:
                # 检查 FTS5 表是否存在
                fts_check = db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='creations_fts'"
                ).fetchone()
                
                if fts_check:
                    # 使用 FTS5 全文搜索（性能提升 90%+）
                    fts_results = db.execute('''
                        SELECT creation_id FROM creations_fts 
                        WHERE creations_fts MATCH ? 
                        ORDER BY rank
                        LIMIT 1000
                    ''', (search,)).fetchall()
                    
                    if fts_results:
                        creation_ids = [r['creation_id'] for r in fts_results]
                        placeholders = ','.join('?' * len(creation_ids))
                        conditions.append(f'id IN ({placeholders})')
                        params.extend(creation_ids)
                    else:
                        # FTS5 搜索无结果，返回空
                        conditions.append('1 = 0')
                else:
                    # FTS5 表不存在，回退到 LIKE 搜索
                    conditions.append('(prompt LIKE ? OR tags LIKE ?)')
                    params.extend([f'%{search}%', f'%{search}%'])
            except Exception:
                # 如果 FTS5 查询失败，回退到 LIKE 搜索
                conditions.append('(prompt LIKE ? OR tags LIKE ?)')
                params.extend([f'%{search}%', f'%{search}%'])

        if is_favorite is not None:
            conditions.append('is_favorite = ?')
            params.append(1 if is_favorite else 0)

        where_clause = ' AND '.join(conditions)
        params.extend([limit, offset])

        creations = db.execute(
            f'''SELECT * FROM creations
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?''',
            params
        ).fetchall()

        return [dict(creation) for creation in creations]

    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """获取用户作品统计信息（优化版：减少查询次数）"""
        db = get_db()

        # 优化：使用单次查询计算 total, favorites, recent_week
        stats = db.execute(
            '''SELECT 
                   COUNT(*) as total,
                   SUM(CASE WHEN is_favorite = 1 THEN 1 ELSE 0 END) as favorites,
                   SUM(CASE WHEN created_at >= datetime('now', '-7 days') THEN 1 ELSE 0 END) as recent_week
               FROM creations 
               WHERE user_id = ?''',
            (user_id,)
        ).fetchone()

        # 按分类统计（保持独立查询，但添加用户过滤）
        categories = db.execute(
            '''SELECT category, COUNT(*) as count
               FROM creations 
               WHERE user_id = ?
               GROUP BY category''',
            (user_id,)
        ).fetchall()

        return {
            'total': stats['total'] or 0,
            'favorites': stats['favorites'] or 0,
            'recent_week': stats['recent_week'] or 0,
            'categories': [dict(cat) for cat in categories]
        }

    @staticmethod
    def update_favorite(creation_id: int, user_id: int, is_favorite: bool) -> bool:
        """更新作品收藏状态"""
        db = get_db()
        result = db.execute(
            '''UPDATE creations SET is_favorite = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?''',
            (1 if is_favorite else 0, creation_id, user_id)
        )
        db.commit()
        return result.rowcount > 0

    @staticmethod
    def update_tags(creation_id: int, user_id: int, tags: str) -> bool:
        """更新作品标签"""
        db = get_db()
        result = db.execute(
            '''UPDATE creations SET tags = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?''',
            (tags, creation_id, user_id)
        )
        db.commit()
        return result.rowcount > 0

    @staticmethod
    def update_category(creation_id: int, user_id: int, category: str) -> bool:
        """更新作品分类"""
        db = get_db()
        result = db.execute(
            '''UPDATE creations SET category = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?''',
            (category, creation_id, user_id)
        )
        db.commit()
        return result.rowcount > 0

    @staticmethod
    def get_available_categories(user_id: int) -> List[str]:
        """获取用户使用过的所有分类"""
        db = get_db()
        categories = db.execute(
            '''SELECT DISTINCT category FROM creations
               WHERE user_id = ? AND category IS NOT NULL
               ORDER BY category''',
            (user_id,)
        ).fetchall()
        return [cat['category'] for cat in categories]

    @staticmethod
    def get_popular_tags(user_id: int, limit: int = 20) -> List[str]:
        """获取用户常用标签"""
        db = get_db()
        # 简单的标签统计，假设标签用逗号分隔
        creations = db.execute(
            'SELECT tags FROM creations WHERE user_id = ? AND tags IS NOT NULL AND tags != ""',
            (user_id,)
        ).fetchall()

        tag_count = {}
        for creation in creations:
            if creation['tags']:
                tags = [tag.strip() for tag in creation['tags'].split(',')]
                for tag in tags:
                    if tag:
                        tag_count[tag] = tag_count.get(tag, 0) + 1

        # 按使用频次排序
        sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags[:limit]]


# === 性能监控与用户行为分析模型类 (Phase 1) ===

class UserSession:
    """用户会话模型"""

    @staticmethod
    def create(user_id: int, session_id: str, ip_address: str = None, user_agent: str = None) -> int:
        """创建新的用户会话"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO user_sessions
               (user_id, session_id, ip_address, user_agent)
               VALUES (?, ?, ?, ?)''',
            (user_id, session_id, ip_address, user_agent)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update_activity(session_id: str, pages_visited: int = None, generations_count: int = None):
        """更新会话活动数据"""
        db = get_db()
        updates = []
        params = []

        if pages_visited is not None:
            updates.append('pages_visited = ?')
            params.append(pages_visited)

        if generations_count is not None:
            updates.append('generations_count = ?')
            params.append(generations_count)

        if updates:
            params.append(session_id)
            db.execute(
                f'UPDATE user_sessions SET {", ".join(updates)} WHERE session_id = ?',
                params
            )
            db.commit()

    @staticmethod
    def end_session(session_id: str):
        """结束用户会话"""
        db = get_db()
        # 计算会话持续时间
        db.execute(
            '''UPDATE user_sessions
               SET logout_time = CURRENT_TIMESTAMP,
                   duration_seconds = CAST((julianday(CURRENT_TIMESTAMP) - julianday(login_time)) * 86400 AS INTEGER),
                   is_active = 0
               WHERE session_id = ? AND is_active = 1''',
            (session_id,)
        )
        db.commit()

    @staticmethod
    def get_active_sessions_count() -> int:
        """获取当前活跃会话数"""
        db = get_db()
        result = db.execute(
            'SELECT COUNT(*) as count FROM user_sessions WHERE is_active = 1'
        ).fetchone()
        return result['count']


class PerformanceMetric:
    """性能指标模型"""

    @staticmethod
    def record(user_id: int = None, operation_type: str = '', model_used: str = None,
               prompt_length: int = None, image_size: str = None, generation_time: float = None,
               api_response_time: float = None, queue_wait_time: float = None,
               success: bool = True, error_type: str = None, error_message: str = None,
               server_load: float = None, memory_usage_mb: int = None) -> int:
        """记录性能指标"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO performance_metrics
               (user_id, operation_type, model_used, prompt_length, image_size,
                generation_time, api_response_time, queue_wait_time, success,
                error_type, error_message, server_load, memory_usage_mb)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, operation_type, model_used, prompt_length, image_size,
             generation_time, api_response_time, queue_wait_time, success,
             error_type, error_message, server_load, memory_usage_mb)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_avg_generation_time(operation_type: str = None, hours: int = 24) -> float:
        """获取平均生成时间（保留2位小数）"""
        db = get_db()

        where_clause = "WHERE success = 1 AND timestamp >= datetime('now', '-{} hours')".format(hours)
        if operation_type:
            where_clause += f" AND operation_type = '{operation_type}'"

        result = db.execute(
            f'''SELECT AVG(generation_time) as avg_time
                FROM performance_metrics {where_clause}
                AND generation_time IS NOT NULL'''
        ).fetchone()

        avg_time = result['avg_time'] or 0.0
        return round(avg_time, 2)

    @staticmethod
    def get_error_rate(hours: int = 24) -> float:
        """获取错误率"""
        db = get_db()
        result = db.execute(
            '''SELECT
                   COUNT(*) as total,
                   SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as errors
               FROM performance_metrics
               WHERE timestamp >= datetime('now', '-{} hours')'''.format(hours)
        ).fetchone()

        if result['total'] == 0:
            return 0.0
        return (result['errors'] / result['total']) * 100

    @staticmethod
    def get_peak_load(hours: int = 24) -> float:
        """获取峰值负载"""
        db = get_db()
        result = db.execute(
            '''SELECT MAX(server_load) as peak_load
               FROM performance_metrics
               WHERE timestamp >= datetime('now', '-{} hours')
               AND server_load IS NOT NULL'''.format(hours)
        ).fetchone()

        return result['peak_load'] or 0.0


class UserBehavior:
    """用户行为分析模型"""

    @staticmethod
    def record(user_id: int, session_id: str = None, action_type: str = '',
               target_id: int = None, parameters: str = None, page_url: str = None,
               referrer: str = None, device_type: str = None, browser: str = None) -> int:
        """记录用户行为"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO user_behaviors
               (user_id, session_id, action_type, target_id, parameters,
                page_url, referrer, device_type, browser)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, session_id, action_type, target_id, parameters,
             page_url, referrer, device_type, browser)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_user_preferences(user_id: int) -> Dict[str, Any]:
        """分析用户偏好"""
        db = get_db()

        # 最常用的模型
        model_result = db.execute(
            '''SELECT parameters, COUNT(*) as count
               FROM user_behaviors
               WHERE user_id = ? AND action_type = 'generate'
               AND parameters IS NOT NULL
               GROUP BY parameters
               ORDER BY count DESC
               LIMIT 1''',
            (user_id,)
        ).fetchone()

        # 最活跃的时间段（小时）
        hour_result = db.execute(
            '''SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, COUNT(*) as count
               FROM user_behaviors
               WHERE user_id = ?
               GROUP BY hour
               ORDER BY count DESC
               LIMIT 1''',
            (user_id,)
        ).fetchone()

        # 平均会话时长
        session_result = db.execute(
            '''SELECT AVG(duration_seconds) as avg_duration
               FROM user_sessions
               WHERE user_id = ? AND duration_seconds IS NOT NULL''',
            (user_id,)
        ).fetchone()

        return {
            'preferred_model': model_result['parameters'] if model_result else None,
            'most_active_hour': hour_result['hour'] if hour_result else None,
            'avg_session_duration': session_result['avg_duration'] if session_result else 0
        }

    @staticmethod
    def get_popular_actions(days: int = 7) -> List[Dict[str, Any]]:
        """获取热门操作统计"""
        db = get_db()
        actions = db.execute(
            '''SELECT action_type, COUNT(*) as count
               FROM user_behaviors
               WHERE timestamp >= datetime('now', '-{} days')
               GROUP BY action_type
               ORDER BY count DESC'''.format(days)
        ).fetchall()

        return [dict(action) for action in actions]


class DailyStat:
    """每日统计模型"""

    @staticmethod
    def update_today():
        """更新今日统计数据"""
        db = get_db()
        today = datetime.now().date().isoformat()

        # 获取今日各项统计数据
        total_users = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']

        active_users = db.execute(
            '''SELECT COUNT(DISTINCT user_id) as count
               FROM user_sessions
               WHERE DATE(login_time) = ?''',
            (today,)
        ).fetchone()['count']

        new_registrations = db.execute(
            '''SELECT COUNT(*) as count
               FROM users
               WHERE DATE(created_at) = ?''',
            (today,)
        ).fetchone()['count']

        total_generations = db.execute(
            '''SELECT COUNT(*) as count
               FROM creations
               WHERE DATE(created_at) = ?''',
            (today,)
        ).fetchone()['count']

        successful_generations = db.execute(
            '''SELECT COUNT(*) as count
               FROM performance_metrics
               WHERE DATE(timestamp) = ? AND operation_type LIKE '%_to_image' AND success = 1''',
            (today,)
        ).fetchone()['count']

        avg_generation_time = PerformanceMetric.get_avg_generation_time(hours=24)
        error_rate = PerformanceMetric.get_error_rate(hours=24)
        peak_concurrent_users = UserSession.get_active_sessions_count()

        # 插入或更新今日统计
        db.execute(
            '''INSERT OR REPLACE INTO daily_stats
               (date, total_users, active_users, new_registrations,
                total_generations, successful_generations, avg_generation_time,
                peak_concurrent_users, error_rate)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (today, total_users, active_users, new_registrations,
             total_generations, successful_generations, avg_generation_time,
             peak_concurrent_users, error_rate)
        )
        db.commit()

    @staticmethod
    def get_weekly_stats() -> List[Dict[str, Any]]:
        """获取最近7天统计数据"""
        db = get_db()
        stats = db.execute(
            '''SELECT * FROM daily_stats
               WHERE date >= date('now', '-7 days')
               ORDER BY date DESC'''
        ).fetchall()

        return [dict(stat) for stat in stats]


class JWTBlacklist:
    """JWT黑名单模型"""

    @staticmethod
    def add(jti: str):
        """添加token到黑名单"""
        db = get_db()
        try:
            db.execute('INSERT INTO jwt_blacklist (jti) VALUES (?)', (jti,))
            db.commit()
        except sqlite3.IntegrityError:
            pass  # JTI已存在

    @staticmethod
    def is_blacklisted(jti: str) -> bool:
        """检查token是否在黑名单中"""
        db = get_db()
        result = db.execute(
            'SELECT 1 FROM jwt_blacklist WHERE jti = ?', (jti,)
        ).fetchone()
        return result is not None

    @staticmethod
    def cleanup_expired():
        """清理过期的黑名单记录（需要定期调用）"""
        db = get_db()
        # 删除7天前的记录
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        db.execute('DELETE FROM jwt_blacklist WHERE created_at < ?', (cutoff,))
        db.commit()


# === Phase 2: 智能推荐系统模型类 ===

class UserPreferences:
    """用户偏好设置模型"""

    @staticmethod
    def get_or_create(user_id: int) -> Dict[str, Any]:
        """获取或创建用户偏好设置"""
        db = get_db()
        prefs = db.execute(
            'SELECT * FROM user_preferences WHERE user_id = ?', (user_id,)
        ).fetchone()

        if not prefs:
            # 创建默认偏好设置
            db.execute(
                '''INSERT INTO user_preferences (user_id) VALUES (?)''',
                (user_id,)
            )
            db.commit()
            prefs = db.execute(
                'SELECT * FROM user_preferences WHERE user_id = ?', (user_id,)
            ).fetchone()

        return dict(prefs) if prefs else None

    @staticmethod
    def update_preference(user_id: int, key: str, value: Any) -> bool:
        """更新单个偏好设置"""
        db = get_db()

        # 确保用户偏好记录存在
        UserPreferences.get_or_create(user_id)

        # 动态构建更新语句
        if key in ['preferred_model', 'preferred_size', 'preferred_quality',
                   'generation_style', 'prompt_language', 'privacy_level']:
            db.execute(
                f'UPDATE user_preferences SET {key} = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                (value, user_id)
            )
        elif key in ['auto_enhance_prompts', 'save_generation_history', 'enable_smart_suggestions']:
            db.execute(
                f'UPDATE user_preferences SET {key} = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                (1 if value else 0, user_id)
            )
        else:
            return False

        db.commit()
        return True

    @staticmethod
    def learn_from_behavior(user_id: int):
        """从用户行为中学习偏好"""
        db = get_db()

        # 分析用户最常用的模型
        model_stats = db.execute(
            '''SELECT model_used, COUNT(*) as count
               FROM creations
               WHERE user_id = ? AND created_at >= datetime('now', '-30 days')
               GROUP BY model_used
               ORDER BY count DESC
               LIMIT 1''',
            (user_id,)
        ).fetchone()

        if model_stats:
            UserPreferences.update_preference(user_id, 'preferred_model', model_stats['model_used'])

        # 分析用户最常用的尺寸
        size_stats = db.execute(
            '''SELECT size, COUNT(*) as count
               FROM creations
               WHERE user_id = ? AND created_at >= datetime('now', '-30 days')
               GROUP BY size
               ORDER BY count DESC
               LIMIT 1''',
            (user_id,)
        ).fetchone()

        if size_stats:
            UserPreferences.update_preference(user_id, 'preferred_size', size_stats['size'])


class SmartRecommendation:
    """智能推荐模型"""

    @staticmethod
    def create_recommendation(user_id: int, recommendation_type: str, original_input: str,
                            recommended_value: str, reason: str, confidence: float = 0.5,
                            context_data: str = None) -> int:
        """创建新的推荐记录"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO smart_recommendations
               (user_id, recommendation_type, original_input, recommended_value,
                recommendation_reason, confidence_score, context_data)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, recommendation_type, original_input, recommended_value,
             reason, confidence, context_data)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_recommendations_for_user(user_id: int, recommendation_type: str = None,
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的推荐记录"""
        db = get_db()

        if recommendation_type:
            recommendations = db.execute(
                '''SELECT * FROM smart_recommendations
                   WHERE user_id = ? AND recommendation_type = ?
                   ORDER BY created_at DESC
                   LIMIT ?''',
                (user_id, recommendation_type, limit)
            ).fetchall()
        else:
            recommendations = db.execute(
                '''SELECT * FROM smart_recommendations
                   WHERE user_id = ?
                   ORDER BY created_at DESC
                   LIMIT ?''',
                (user_id, limit)
            ).fetchall()

        return [dict(rec) for rec in recommendations]

    @staticmethod
    def record_user_action(recommendation_id: int, action: str, effectiveness_score: float = None):
        """记录用户对推荐的反应"""
        db = get_db()
        updates = ['user_action = ?', 'acted_at = CURRENT_TIMESTAMP']
        params = [action]

        if effectiveness_score is not None:
            updates.append('effectiveness_score = ?')
            params.append(effectiveness_score)

        params.append(recommendation_id)

        db.execute(
            f'UPDATE smart_recommendations SET {", ".join(updates)} WHERE id = ?',
            params
        )
        db.commit()

    @staticmethod
    def generate_model_recommendation(user_id: int, current_prompt: str) -> Optional[Dict[str, Any]]:
        """基于用户历史生成模型推荐"""
        db = get_db()

        # 获取用户偏好
        prefs = UserPreferences.get_or_create(user_id)

        # 分析提示词特征
        prompt_length = len(current_prompt)

        # 基于提示词长度和用户历史推荐模型
        if prompt_length > 100:
            # 长提示词推荐高质量模型
            recommended_model = 'nano-banana-hd'
            reason = "检测到详细的提示词，建议使用高清模型获得更好的细节表现"
            confidence = 0.8
        elif prefs['preferred_model'] != 'nano-banana':
            # 使用用户偏好模型
            recommended_model = prefs['preferred_model']
            reason = f"基于您的使用习惯，推荐使用 {recommended_model} 模型"
            confidence = 0.7
        else:
            return None

        return {
            'type': 'model',
            'value': recommended_model,
            'reason': reason,
            'confidence': confidence
        }


class PromptOptimization:
    """提示词优化模型"""

    @staticmethod
    def optimize_prompt(original_prompt: str, user_id: int = None) -> Dict[str, Any]:
        """优化提示词"""
        import json

        # 基础优化规则
        optimized = original_prompt.strip()
        improvements = []
        keywords_added = []

        # 检查是否包含质量关键词
        quality_keywords = ['高质量', 'detailed', 'high quality', '4K', '8K', 'masterpiece']
        if not any(kw in optimized.lower() for kw in [kw.lower() for kw in quality_keywords]):
            optimized += ", high quality, detailed"
            keywords_added.extend(['high quality', 'detailed'])
            improvements.append("添加质量提升关键词")

        # 检查是否包含风格关键词
        style_keywords = ['realistic', 'artistic', 'anime', 'cartoon', '写实', '艺术风格']
        if not any(kw in optimized.lower() for kw in [kw.lower() for kw in style_keywords]):
            optimized += ", realistic style"
            keywords_added.append('realistic style')
            improvements.append("添加默认风格标签")

        # 如果有用户偏好，应用个性化优化
        if user_id:
            prefs = UserPreferences.get_or_create(user_id)
            if prefs.get('generation_style'):
                style = prefs['generation_style']
                if style not in optimized.lower():
                    optimized += f", {style} style"
                    keywords_added.append(f'{style} style')
                    improvements.append(f"应用用户偏好风格: {style}")

        return {
            'original': original_prompt,
            'optimized': optimized,
            'improvements': improvements,
            'keywords_added': keywords_added,
            'optimization_type': 'enhancement'
        }

    @staticmethod
    def save_optimization(optimization_data: Dict[str, Any]) -> int:
        """保存优化记录"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO prompt_optimizations
               (original_prompt, optimized_prompt, optimization_type,
                improvement_description, keywords_added)
               VALUES (?, ?, ?, ?, ?)''',
            (optimization_data['original'],
             optimization_data['optimized'],
             optimization_data['optimization_type'],
             '; '.join(optimization_data['improvements']),
             ', '.join(optimization_data['keywords_added']))
        )
        db.commit()
        return cursor.lastrowid


class CreationSimilarity:
    """作品相似性分析模型"""

    @staticmethod
    def calculate_prompt_similarity(prompt1: str, prompt2: str) -> float:
        """计算提示词相似度"""
        # 简单的关键词匹配算法
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    def find_similar_creations(creation_id: int, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """为用户找到相似的作品"""
        db = get_db()

        # 获取目标作品信息
        target = db.execute(
            'SELECT * FROM creations WHERE id = ?', (creation_id,)
        ).fetchone()

        if not target:
            return []

        # 获取用户的其他作品
        other_creations = db.execute(
            '''SELECT * FROM creations
               WHERE user_id = ? AND id != ?
               ORDER BY created_at DESC''',
            (user_id, creation_id)
        ).fetchall()

        # 计算相似度
        similar_creations = []
        for creation in other_creations:
            similarity = CreationSimilarity.calculate_prompt_similarity(
                target['prompt'], creation['prompt']
            )

            if similarity > 0.3:  # 相似度阈值
                similar_creations.append({
                    'creation': dict(creation),
                    'similarity_score': similarity,
                    'similarity_type': 'prompt'
                })

        # 按相似度排序并返回前N个
        similar_creations.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_creations[:limit]


class RecommendationAnalytics:
    """推荐效果分析模型"""

    @staticmethod
    def update_daily_analytics():
        """更新每日推荐效果统计"""
        db = get_db()
        today = datetime.now().date().isoformat()

        # 获取各类推荐的统计数据
        recommendation_types = ['model', 'size', 'prompt_enhancement', 'style', 'similar_creations']

        for rec_type in recommendation_types:
            # 总推荐数
            total = db.execute(
                '''SELECT COUNT(*) as count FROM smart_recommendations
                   WHERE DATE(created_at) = ? AND recommendation_type = ?''',
                (today, rec_type)
            ).fetchone()['count']

            # 接受的推荐数
            accepted = db.execute(
                '''SELECT COUNT(*) as count FROM smart_recommendations
                   WHERE DATE(created_at) = ? AND recommendation_type = ?
                   AND user_action = 'accepted' ''',
                (today, rec_type)
            ).fetchone()['count']

            # 拒绝的推荐数
            rejected = db.execute(
                '''SELECT COUNT(*) as count FROM smart_recommendations
                   WHERE DATE(created_at) = ? AND recommendation_type = ?
                   AND user_action = 'rejected' ''',
                (today, rec_type)
            ).fetchone()['count']

            # 计算接受率
            acceptance_rate = (accepted / total * 100) if total > 0 else 0

            # 平均置信度
            avg_confidence = db.execute(
                '''SELECT AVG(confidence_score) as avg_conf FROM smart_recommendations
                   WHERE DATE(created_at) = ? AND recommendation_type = ?''',
                (today, rec_type)
            ).fetchone()['avg_conf'] or 0

            # 插入或更新统计数据
            db.execute(
                '''INSERT OR REPLACE INTO recommendation_analytics
                   (date, recommendation_type, total_recommendations,
                    accepted_recommendations, rejected_recommendations,
                    acceptance_rate, avg_confidence_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (today, rec_type, total, accepted, rejected, acceptance_rate, avg_confidence)
            )

        db.commit()

    @staticmethod
    def get_analytics_summary(days: int = 7) -> List[Dict[str, Any]]:
        """获取推荐效果汇总"""
        db = get_db()
        analytics = db.execute(
            '''SELECT * FROM recommendation_analytics
               WHERE date >= date('now', '-{} days')
               ORDER BY date DESC, recommendation_type'''.format(days)
        ).fetchall()

        return [dict(record) for record in analytics]


class SystemSettings:
    """系统配置模型"""

    @staticmethod
    def get(key: str) -> Optional[str]:
        """
        获取配置值

        Args:
            key: 配置键名

        Returns:
            配置值（如果加密则自动解密），未找到返回None
        """
        db = get_db()
        setting = db.execute(
            'SELECT value, is_encrypted FROM system_settings WHERE key = ?',
            (key,)
        ).fetchone()

        if not setting:
            return None

        value = setting['value']
        is_encrypted = setting['is_encrypted']

        # 如果加密，则解密
        if is_encrypted and value:
            from app.utils.encryption import ConfigEncryption
            value = ConfigEncryption.decrypt(value)

        return value

    @staticmethod
    def set(key: str, value: str, description: str = '', is_encrypted: bool = False, updated_by: int = None) -> bool:
        """
        设置配置值

        Args:
            key: 配置键名
            value: 配置值
            description: 配置说明
            is_encrypted: 是否加密存储
            updated_by: 更新者用户ID

        Returns:
            True if successful
        """
        db = get_db()

        # 如果需要加密，先加密
        stored_value = value
        if is_encrypted and value:
            from app.utils.encryption import ConfigEncryption
            stored_value = ConfigEncryption.encrypt(value)

        try:
            db.execute(
                '''INSERT OR REPLACE INTO system_settings
                   (key, value, description, is_encrypted, updated_by, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (key, stored_value, description, 1 if is_encrypted else 0,
                 updated_by, datetime.now().isoformat())
            )
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"设置配置失败: {str(e)}")
            return False

    @staticmethod
    def get_all(mask_encrypted: bool = True) -> List[Dict[str, Any]]:
        """
        获取所有配置

        Args:
            mask_encrypted: 是否脱敏显示加密值

        Returns:
            配置列表
        """
        db = get_db()
        settings = db.execute(
            '''SELECT id, key, value, description, is_encrypted, updated_by, updated_at
               FROM system_settings ORDER BY key'''
        ).fetchall()

        result = []
        for setting in settings:
            setting_dict = dict(setting)

            # 如果是加密字段且需要脱敏
            if setting_dict['is_encrypted'] and mask_encrypted and setting_dict['value']:
                from app.utils.encryption import ConfigEncryption
                # 先解密
                decrypted = ConfigEncryption.decrypt(setting_dict['value'])
                # 再脱敏
                setting_dict['value'] = ConfigEncryption.mask_api_key(decrypted)
                setting_dict['is_masked'] = True
            else:
                setting_dict['is_masked'] = False

            result.append(setting_dict)

        return result

    @staticmethod
    def delete(key: str) -> bool:
        """删除配置"""
        db = get_db()
        try:
            db.execute('DELETE FROM system_settings WHERE key = ?', (key,))
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    @staticmethod
    def initialize_defaults():
        """初始化默认配置"""
        defaults = [
            {
                'key': 'openai_hk_base_url',
                'value': 'https://api.openai-hk.com',
                'description': 'nano-banana API Base URL',
                'is_encrypted': False
            },
            {
                'key': 'openai_hk_api_key',
                'value': '',  # 初始为空，需要管理员配置
                'description': 'nano-banana API Key（加密存储）',
                'is_encrypted': True
            }
        ]

        for default in defaults:
            # 检查是否已存在
            existing = SystemSettings.get(default['key'])
            if existing is None:
                SystemSettings.set(
                    key=default['key'],
                    value=default['value'],
                    description=default['description'],
                    is_encrypted=default['is_encrypted']
                )


def init_app(app):
    """初始化数据库应用"""
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
        # 初始化默认配置
        SystemSettings.initialize_defaults()