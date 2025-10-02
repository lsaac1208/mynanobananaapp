#!/usr/bin/env python3
"""
重置数据库并创建管理员账户
"""
import os
import sys
import hashlib
from pathlib import Path

# 添加后端路径
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app import create_app
from app.database import get_db, init_db

def hash_password(password: str) -> str:
    """SHA256密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_and_initialize():
    """重置数据库并初始化"""
    os.chdir(backend_path)

    # 删除旧数据库
    db_path = Path('instance/database.db')
    if db_path.exists():
        print(f"删除旧数据库: {db_path}")
        db_path.unlink()

    # 创建Flask应用
    app = create_app()

    with app.app_context():
        # 初始化数据库结构
        print("\n初始化数据库结构...")
        init_db()
        print("✅ 数据库结构创建完成")

        # 创建管理员账户
        print("\n创建管理员账户...")
        db = get_db()

        admin_email = 'a84822289@gmail.com'
        admin_password = 'Wl$19891208'
        admin_password_hash = hash_password(admin_password)

        db.execute('''
            INSERT INTO users (email, password_hash, credits, is_active)
            VALUES (?, ?, ?, ?)
        ''', (admin_email, admin_password_hash, 100, 1))

        db.commit()

        print(f"✅ 管理员账户创建成功:")
        print(f"   邮箱: {admin_email}")
        print(f"   密码: {admin_password}")
        print(f"   初始次数: 100")

        # 验证创建
        user = db.execute('SELECT * FROM users WHERE id = 1').fetchone()
        print(f"\n验证结果:")
        print(f"   用户ID: {user['id']}")
        print(f"   邮箱: {user['email']}")
        print(f"   次数: {user['credits']}")
        print(f"   状态: {'激活' if user['is_active'] else '未激活'}")

        # 显示所有表
        print(f"\n数据库表列表:")
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table['name']}")

        print(f"\n✅ 数据库重置完成！")
        print(f"\n可以使用以下凭据登录:")
        print(f"   账号: {admin_email}")
        print(f"   密码: {admin_password}")

if __name__ == '__main__':
    reset_and_initialize()
