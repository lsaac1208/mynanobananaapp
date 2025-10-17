#!/usr/bin/env python3
"""
FTS5 全文搜索迁移应用脚本
用于将 FTS5 全文搜索功能应用到数据库

使用方法：
    python apply_fts_search.py [--force]
    
参数：
    --force  强制重新创建（跳过确认）
"""

import sqlite3
import os
import sys


def apply_fts_search(force=False):
    """应用 FTS5 全文搜索迁移"""
    
    # 获取脚本所在目录的父目录（backend目录）
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(backend_dir, 'instance', 'database.db')
    sql_file = os.path.join(os.path.dirname(__file__), 'add_fts_search.sql')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"❌ 错误：数据库文件不存在: {db_path}")
        print(f"   请确保应用已初始化并创建了数据库")
        sys.exit(1)
    
    # 检查 SQL 文件是否存在
    if not os.path.exists(sql_file):
        print(f"❌ 错误：SQL 迁移文件不存在: {sql_file}")
        sys.exit(1)
    
    print("🔄 开始应用 FTS5 全文搜索迁移...")
    print(f"   数据库路径: {db_path}")
    print(f"   SQL 文件: {sql_file}")
    print()
    
    try:
        # 读取 SQL 脚本
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查 FTS5 是否已经存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='creations_fts'
        """)
        fts_exists = cursor.fetchone()
        
        if fts_exists:
            print("⚠️  警告：FTS5 表已存在")
            if not force:
                response = input("   是否要重新创建？这将删除现有的 FTS5 表。(y/N): ")
                if response.lower() != 'y':
                    print("❌ 迁移已取消")
                    conn.close()
                    sys.exit(0)
            else:
                print("   --force 模式：将强制重新创建")
            
            # 删除现有的 FTS5 表和触发器
            print("🗑️  删除现有 FTS5 表和触发器...")
            cursor.execute("DROP TRIGGER IF EXISTS creations_fts_insert")
            cursor.execute("DROP TRIGGER IF EXISTS creations_fts_update")
            cursor.execute("DROP TRIGGER IF EXISTS creations_fts_delete")
            cursor.execute("DROP TABLE IF EXISTS creations_fts")
            conn.commit()
        
        # 执行 SQL 脚本
        print("📝 执行 SQL 迁移脚本...")
        conn.executescript(sql_script)
        conn.commit()
        
        # 验证迁移结果
        print("✅ 验证迁移结果...")
        
        # 检查 FTS5 表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='creations_fts'
        """)
        if not cursor.fetchone():
            raise Exception("FTS5 表未成功创建")
        print("   ✓ FTS5 表创建成功")
        
        # 检查触发器
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='trigger' AND name LIKE 'creations_fts_%'
        """)
        triggers = cursor.fetchall()
        if len(triggers) != 3:
            raise Exception(f"触发器创建不完整，预期 3 个，实际 {len(triggers)} 个")
        print(f"   ✓ {len(triggers)} 个触发器创建成功")
        
        # 统计导入的数据
        cursor.execute("SELECT COUNT(*) as count FROM creations")
        total_creations = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM creations_fts")
        total_fts = cursor.fetchone()['count']
        
        print(f"   ✓ 数据导入成功: {total_fts} / {total_creations} 条记录")
        
        if total_fts != total_creations:
            print(f"   ⚠️  警告：FTS 记录数与作品数不一致")
        
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ FTS5 全文搜索迁移应用成功！")
        print()
        print("📊 迁移统计:")
        print(f"   - 总作品数: {total_creations}")
        print(f"   - FTS索引数: {total_fts}")
        print(f"   - 触发器数: {len(triggers)}")
        print()
        print("🎯 性能优化:")
        print("   - 搜索速度预计提升 90%+")
        print("   - 支持多关键词搜索")
        print("   - 自动同步新数据")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    # 检查命令行参数
    force = '--force' in sys.argv
    apply_fts_search(force=force)

