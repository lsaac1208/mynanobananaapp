#!/usr/bin/env python3
"""
安全的数据库索引应用工具
只为已存在的表创建索引
"""
import sqlite3
import os
from pathlib import Path

def get_db_path():
    """获取数据库路径"""
    backend_dir = Path(__file__).parent.parent
    db_path = backend_dir / 'instance' / 'database.db'
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        exit(1)
    return str(db_path)

def get_existing_tables(cursor):
    """获取数据库中已存在的表"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]

def get_table_stats(cursor):
    """获取各表的行数统计"""
    existing_tables = get_existing_tables(cursor)
    stats = {}
    for table in existing_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        stats[table] = count
    return stats

def apply_indexes_safe():
    """安全地应用索引"""
    db_path = get_db_path()
    
    print("=" * 60)
    print("数据库性能索引应用工具（安全版本）")
    print("=" * 60)
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表统计信息
        print("=" * 60)
        print("表统计信息")
        print("=" * 60)
        table_stats = get_table_stats(cursor)
        for table, count in sorted(table_stats.items()):
            print(f"{table:30} {count:5} 行")
        
        # 获取数据库大小
        db_size = os.path.getsize(db_path) / 1024 / 1024
        print(f"📁 数据库路径: {db_path}")
        print(f"📊 数据库大小: {db_size:.2f} MB")
        print()
        
        print("=" * 60)
        print("开始应用性能索引（仅为已存在的表）")
        print("=" * 60)
        print()
        
        existing_tables = get_existing_tables(cursor)
        
        # 定义索引SQL（按表分组）
        indexes = {
            'creations': [
                ("idx_creations_user_created", "CREATE INDEX IF NOT EXISTS idx_creations_user_created ON creations(user_id, created_at DESC)"),
                ("idx_creations_category", "CREATE INDEX IF NOT EXISTS idx_creations_category ON creations(category) WHERE category IS NOT NULL"),
                ("idx_creations_favorite", "CREATE INDEX IF NOT EXISTS idx_creations_favorite ON creations(user_id, is_favorite) WHERE is_favorite = 1"),
                ("idx_creations_tags", "CREATE INDEX IF NOT EXISTS idx_creations_tags ON creations(tags) WHERE tags IS NOT NULL AND tags != ''"),
                ("idx_creations_composite", "CREATE INDEX IF NOT EXISTS idx_creations_composite ON creations(user_id, category, created_at DESC)"),
            ],
            'performance_metrics': [
                ("idx_performance_timestamp", "CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp DESC)"),
                ("idx_performance_user_operation", "CREATE INDEX IF NOT EXISTS idx_performance_user_operation ON performance_metrics(user_id, operation_type, timestamp DESC)"),
                ("idx_performance_success", "CREATE INDEX IF NOT EXISTS idx_performance_success ON performance_metrics(success, timestamp DESC)"),
                ("idx_performance_operation", "CREATE INDEX IF NOT EXISTS idx_performance_operation ON performance_metrics(operation_type, timestamp DESC)"),
            ],
            'user_sessions': [
                ("idx_sessions_user_active", "CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON user_sessions(user_id, is_active, login_time DESC)"),
                ("idx_sessions_time_range", "CREATE INDEX IF NOT EXISTS idx_sessions_time_range ON user_sessions(login_time DESC, logout_time DESC)"),
            ],
            'daily_stats': [
                ("idx_daily_stats_date", "CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date DESC)"),
                ("idx_daily_stats_user_date", "CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date ON daily_stats(user_id, date DESC)"),
            ],
            'jwt_blacklist': [
                ("idx_jwt_blacklist_jti", "CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_jti ON jwt_blacklist(jti)"),
                ("idx_jwt_blacklist_created", "CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_created ON jwt_blacklist(created_at DESC)"),
            ],
            'users': [
                ("idx_users_last_login", "CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login_at DESC) WHERE last_login_at IS NOT NULL"),
                ("idx_users_active", "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active, created_at DESC)"),
            ],
        }
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for table, table_indexes in indexes.items():
            if table in existing_tables:
                print(f"\n📋 表 [{table}] 存在，应用索引...")
                for index_name, sql in table_indexes:
                    try:
                        cursor.execute(sql)
                        print(f"  ✅ 创建索引: {index_name}")
                        success_count += 1
                    except sqlite3.OperationalError as e:
                        if 'no such column' in str(e).lower():
                            print(f"  ⚠️  跳过索引: {index_name} (字段不存在)")
                            skip_count += 1
                        else:
                            print(f"  ❌ 失败: {index_name} - {str(e)}")
                            error_count += 1
            else:
                print(f"\n⏭️  表 [{table}] 不存在，跳过 {len(table_indexes)} 个索引")
                skip_count += len(table_indexes)
        
        # 更新查询优化器统计信息
        print("\n📊 更新查询优化器统计信息...")
        cursor.execute("ANALYZE")
        print("✅ 统计信息已更新")
        
        # 提交事务
        conn.commit()
        print()
        print("=" * 60)
        print("✅ 索引应用完成")
        print("=" * 60)
        print(f"成功: {success_count} 个")
        print(f"跳过: {skip_count} 个")
        print(f"失败: {error_count} 个")
        print()
        
        # 显示所有索引
        print("=" * 60)
        print("当前数据库索引列表")
        print("=" * 60)
        cursor.execute("""
            SELECT name, tbl_name 
            FROM sqlite_master 
            WHERE type='index' 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name, name
        """)
        
        current_table = None
        for index_name, table_name in cursor.fetchall():
            if table_name != current_table:
                print(f"\n[{table_name}]")
                current_table = table_name
            print(f"  - {index_name}")
        
        print()
        
    except sqlite3.Error as e:
        print(f"\n❌ 数据库错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 应用索引失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()
    
    return error_count == 0

if __name__ == "__main__":
    import sys
    success = apply_indexes_safe()
    sys.exit(0 if success else 1)

