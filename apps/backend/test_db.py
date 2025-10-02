#!/usr/bin/env python3
"""
测试数据库连接脚本
"""
import os
import sqlite3
from app import create_app, db
from app.models import User

def test_database_connection():
    """测试数据库连接"""
    print("=== 数据库连接测试 ===")

    # 测试应用配置
    app = create_app()
    print(f"Flask应用数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # 检查数据库文件路径
    if 'sqlite:///' in app.config['SQLALCHEMY_DATABASE_URI']:
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"数据库文件路径: {db_path}")
        print(f"数据库文件存在: {os.path.exists(db_path)}")

        if os.path.exists(db_path):
            print(f"文件大小: {os.path.getsize(db_path)} bytes")
            print(f"文件权限: {oct(os.stat(db_path).st_mode)}")

            # 测试直接SQLite连接
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"数据库表: {tables}")
                conn.close()
                print("✓ 直接SQLite连接成功")
            except Exception as e:
                print(f"✗ 直接SQLite连接失败: {e}")

        # 测试目录权限
        db_dir = os.path.dirname(db_path)
        print(f"数据库目录: {db_dir}")
        print(f"目录存在: {os.path.exists(db_dir)}")
        if os.path.exists(db_dir):
            print(f"目录权限: {oct(os.stat(db_dir).st_mode)}")
            print(f"目录可写: {os.access(db_dir, os.W_OK)}")

    # 测试Flask应用数据库连接
    try:
        with app.app_context():
            # 尝试创建表
            db.create_all()
            print("✓ Flask数据库表创建成功")

            # 尝试查询
            users = User.query.all()
            print(f"✓ 用户查询成功，用户数量: {len(users)}")

    except Exception as e:
        print(f"✗ Flask数据库连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()