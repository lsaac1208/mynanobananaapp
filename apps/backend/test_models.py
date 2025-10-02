"""
数据模型测试脚本
"""
from app import create_app, db
from app.models import User, Creation


def test_models():
    """测试数据模型"""
    app = create_app()

    with app.app_context():
        print("🧪 开始测试数据模型...")

        # 测试用户模型
        print("\n👤 测试用户模型:")

        # 创建测试用户
        test_user = User(email='test@example.com', password='test123')
        db.session.add(test_user)
        db.session.commit()

        print(f"✅ 创建用户: {test_user}")
        print(f"📧 邮箱: {test_user.email}")
        print(f"💰 初始次数: {test_user.credits}")

        # 测试密码验证
        assert test_user.check_password('test123'), "密码验证失败"
        assert not test_user.check_password('wrong'), "密码验证应该失败"
        print("✅ 密码验证功能正常")

        # 测试次数管理
        test_user.add_credits(10)
        assert test_user.credits == 10, "添加次数失败"
        print(f"✅ 添加次数后: {test_user.credits}")

        success = test_user.consume_credit()
        assert success and test_user.credits == 9, "消费次数失败"
        print(f"✅ 消费次数后: {test_user.credits}")

        # 测试作品模型
        print("\n🎨 测试作品模型:")

        test_creation = Creation(
            user_id=test_user.id,
            prompt="a beautiful sunset",
            image_url="https://example.com/image.jpg",
            model_used="nano-banana",
            size="1:1"
        )
        db.session.add(test_creation)
        db.session.commit()

        print(f"✅ 创建作品: {test_creation}")
        print(f"🎨 提示词: {test_creation.prompt}")
        print(f"🖼️ 图片URL: {test_creation.image_url}")

        # 测试关系
        user_creations = test_user.creations
        assert len(user_creations) == 1, "用户作品关系错误"
        assert user_creations[0].id == test_creation.id, "作品关联错误"
        print("✅ 用户-作品关系正常")

        # 测试to_dict方法
        user_dict = test_user.to_dict()
        creation_dict = test_creation.to_dict()

        assert 'id' in user_dict and 'email' in user_dict, "用户字典转换失败"
        assert 'id' in creation_dict and 'prompt' in creation_dict, "作品字典转换失败"
        print("✅ 字典转换功能正常")

        # 清理测试数据
        db.session.delete(test_creation)
        db.session.delete(test_user)
        db.session.commit()

        print("\n🎉 所有测试通过！数据模型工作正常")


if __name__ == '__main__':
    test_models()