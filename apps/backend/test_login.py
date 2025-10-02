#!/usr/bin/env python3
"""测试登录功能"""
import sys
import hashlib
from pathlib import Path

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app import create_app
from app.database import User, get_db

def test_login():
    app = create_app()

    with app.app_context():
        db = get_db()

        # 查看用户
        user = db.execute('SELECT * FROM users WHERE id = 1').fetchone()
        print("数据库中的用户:")
        print(f"  ID: {user['id']}")
        print(f"  Email: {user['email']}")
        print(f"  Password Hash: {user['password_hash']}")
        print(f"  Active: {user['is_active']}")

        # 测试密码
        password = 'Wl$19891208'
        print(f"\n测试密码: {password}")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"计算的哈希: {password_hash}")
        print(f"匹配: {user['password_hash'] == password_hash}")

        # 使用User.get_by_email
        user2 = User.get_by_email('a84822289@gmail.com')
        print(f"\nUser.get_by_email 结果:")
        if user2:
            print(f"  找到用户: {user2['email']}")
            print(f"  密码验证: {User.verify_password(user2, password)}")
        else:
            print("  未找到用户！")

        # 检查登录尝试记录
        attempts = db.execute(
            "SELECT * FROM sqlite_master WHERE type='table' AND name='login_attempts'"
        ).fetchone()
        print(f"\nlogin_attempts 表存在: {attempts is not None}")

if __name__ == '__main__':
    test_login()
