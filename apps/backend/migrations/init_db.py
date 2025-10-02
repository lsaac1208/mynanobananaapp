"""
数据库初始化脚本
"""
from app import create_app, db
from app.models import User, Creation


def init_database():
    """初始化数据库"""
    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()

        print("✅ 数据库表创建成功")
        print("📊 已创建的表:")
        print("  - users (用户表)")
        print("  - creations (作品表)")

        # 检查是否有管理员用户，如果没有就创建一个测试用户
        if not User.query.filter_by(email='admin@test.com').first():
            admin_user = User(email='admin@test.com', password='admin123')
            admin_user.credits = 100  # 给管理员用户100次
            db.session.add(admin_user)
            db.session.commit()
            print("👤 创建测试管理员用户: admin@test.com (密码: admin123)")
            print("💰 初始次数: 100")


if __name__ == '__main__':
    init_database()