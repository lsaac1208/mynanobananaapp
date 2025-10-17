#!/usr/bin/env python3
"""
配置诊断脚本 - 检查环境变量和Flask配置是否正确
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("Nano-Banana 配置诊断")
print("=" * 60)

# 加载.env文件
env_file = os.path.join(os.path.dirname(__file__), '.env')
print(f"\n1. 检查.env文件: {env_file}")
print(f"   文件存在: {os.path.exists(env_file)}")

load_dotenv()

# 检查关键环境变量
print("\n2. 环境变量检查:")
env_vars = {
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
    'ENCRYPTION_KEY': os.getenv('ENCRYPTION_KEY'),
    'OPENAI_HK_API_KEY': os.getenv('OPENAI_HK_API_KEY'),
    'CORS_ORIGINS': os.getenv('CORS_ORIGINS'),
    'FLASK_ENV': os.getenv('FLASK_ENV')
}

for key, value in env_vars.items():
    if value:
        if 'KEY' in key and len(value) > 20:
            display_value = value[:10] + '...' + value[-10:]
        else:
            display_value = value
        print(f"   ✅ {key}: {display_value}")
    else:
        print(f"   ❌ {key}: 未设置")

# 检查Flask配置
print("\n3. Flask应用配置:")
try:
    from app import create_app
    app = create_app()
    
    with app.app_context():
        print(f"   ✅ SECRET_KEY: {app.config['SECRET_KEY'][:10]}...")
        print(f"   ✅ JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY'][:10]}...")
        print(f"   ✅ CORS_ORIGINS: {app.config['CORS_ORIGINS']}")
        print(f"   ✅ DEBUG: {app.config.get('DEBUG', False)}")
        print(f"   ✅ TESTING: {app.config.get('TESTING', False)}")
        
except Exception as e:
    print(f"   ❌ 创建应用失败: {e}")

# 检查数据库
print("\n4. 数据库检查:")
try:
    from app.database import get_db
    with app.app_context():
        db = get_db()
        user_count = db.execute('SELECT COUNT(*) as count FROM users').fetchone()
        print(f"   ✅ 用户数量: {user_count['count']}")
        
        admin = db.execute('SELECT * FROM users WHERE id = 1').fetchone()
        if admin:
            print(f"   ✅ 管理员存在: {admin['email']}")
        else:
            print(f"   ❌ 管理员不存在（ID=1）")
            
except Exception as e:
    print(f"   ❌ 数据库检查失败: {e}")

# JWT测试
print("\n5. JWT令牌测试:")
try:
    from flask_jwt_extended import create_access_token
    with app.app_context():
        test_token = create_access_token(identity=1)
        print(f"   ✅ 生成测试token: {test_token[:50]}...")
        
        # 尝试验证token
        from flask_jwt_extended import decode_token
        decoded = decode_token(test_token)
        print(f"   ✅ Token解码成功: user_id={decoded['sub']}")
        
except Exception as e:
    print(f"   ❌ JWT测试失败: {e}")

print("\n" + "=" * 60)
print("诊断完成！")
print("=" * 60)

