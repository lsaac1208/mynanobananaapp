#!/usr/bin/env python3
"""
修复 creations 表的 user_id 约束 - 允许 NULL 以支持孤儿作品
"""
import sqlite3
import os

def fix_user_id_constraint():
    """修改 user_id 字段允许 NULL"""
    db_path = 'instance/database.db'

    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("开始修复 user_id 约束...")

        # 1. 开始事务
        cursor.execute('BEGIN TRANSACTION')

        # 2. 创建新表 (user_id 允许 NULL)
        cursor.execute('''
            CREATE TABLE creations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
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
                is_orphaned BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        print("✅ 创建新表 creations_new")

        # 3. 复制数据
        cursor.execute('''
            INSERT INTO creations_new
            SELECT * FROM creations
        ''')
        rows_copied = cursor.rowcount
        print(f"✅ 复制 {rows_copied} 行数据")

        # 4. 删除旧表
        cursor.execute('DROP TABLE creations')
        print("✅ 删除旧表 creations")

        # 5. 重命名新表
        cursor.execute('ALTER TABLE creations_new RENAME TO creations')
        print("✅ 重命名新表为 creations")

        # 6. 提交事务
        conn.commit()
        print("✅ 提交事务完成")

        # 7. 验证新结构
        cursor.execute("PRAGMA table_info(creations)")
        columns = cursor.fetchall()
        user_id_col = [col for col in columns if col[1] == 'user_id'][0]
        is_nullable = user_id_col[3] == 0  # notnull 字段为 0 表示允许 NULL
        print(f"\n验证结果:")
        print(f"  user_id 字段允许 NULL: {is_nullable}")
        print(f"  表结构: {columns}")

        print("\n✅ 修复完成!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    os.chdir('/Users/wang/Documents/MyCode/mynanobananaapp/apps/backend')
    fix_user_id_constraint()
