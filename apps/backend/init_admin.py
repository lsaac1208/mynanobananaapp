#!/usr/bin/env python3
"""
初始化数据库并创建管理员账户
"""
import os
import sys
from pathlib import Path

# 设置环境变量
os.environ['ENCRYPTION_MASTER_KEY'] = 'i3N5RYqusUuKU7Orhq8AxOBDYWoIkqF7pyqPIFBncMA='
os.environ['ENCRYPTION_SALT'] = '0CmHxpsIU9m3Arky1_V4V390xoz0VZ8XWdzfOMn_3n8='

# 添加项目路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.database import User, get_db

def init_admin():
    """初始化管理员账户"""
    print("=" * 60)
    print("数据库初始化 - 创建管理员账户")
    print("=" * 60)
    print()
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        # 管理员信息
        admin_email = 'a84822289@gmail.com'
        admin_password = 'Wl$19891208'
        
        try:
            conn = get_db()
            cursor = conn.cursor()
        
            # 检查管理员是否已存在
            existing_admin = User.get_by_email(admin_email)
            if existing_admin:
                print(f"⚠️  管理员账户已存在: {admin_email}")
                print(f"📧 邮箱: {admin_email}")
                print(f"👤 用户ID: {existing_admin['id']}")
                print(f"💰 积分余额: {existing_admin['credits']}")
                print()
                print("✅ 您可以直接使用此账户登录！")
                return True
            
            # 创建管理员账户
            print(f"📧 创建管理员账户...")
            print(f"   邮箱: {admin_email}")
            print(f"   密码: {'*' * len(admin_password)}")
            print()
            
            # 使用User.create方法（会自动使用新的PBKDF2哈希）
            admin_user = User.create(
                email=admin_email,
                password=admin_password,
                credits=1000  # 给管理员1000积分
            )
            
            if admin_user:
                print("=" * 60)
                print("✅ 管理员账户创建成功！")
                print("=" * 60)
                print(f"📧 邮箱: {admin_email}")
                print(f"🔑 密码: {admin_password}")
                print(f"👤 用户ID: {admin_user['id']}")
                print(f"💰 初始积分: {admin_user['credits']}")
                print(f"📅 创建时间: {admin_user['created_at']}")
                print()
                print("⚠️  请妥善保管管理员账户信息！")
                print()
                
                # 检查是否需要设置为管理员角色
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
                if cursor.fetchone():
                    print("🔐 检测到角色系统，设置管理员角色...")
                    
                    # 检查admin角色是否存在
                    cursor.execute("SELECT id FROM roles WHERE name='admin'")
                    admin_role = cursor.fetchone()
                    
                    if admin_role:
                        admin_role_id = admin_role[0]
                        # 检查用户是否已有角色
                        cursor.execute("SELECT * FROM user_roles WHERE user_id=?", (admin_user['id'],))
                        if not cursor.fetchone():
                            # 分配管理员角色
                            cursor.execute(
                                "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
                                (admin_user['id'], admin_role_id)
                            )
                            conn.commit()
                            print("✅ 已分配管理员角色")
                        else:
                            print("ℹ️  用户已有角色")
                    else:
                        print("⚠️  admin角色不存在，需要先运行角色系统迁移")
                
                return True
            else:
                print("❌ 创建管理员账户失败")
                return False
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    init_admin()
