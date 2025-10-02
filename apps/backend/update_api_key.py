#!/usr/bin/env python3
"""
更新API密钥脚本
使用方法: python3 update_api_key.py YOUR_NEW_API_KEY
"""
import sys
from app import create_app
from app.services.encryption_service import encryption_service
from app.repositories.api_config_repository import APIConfigRepository

def update_api_key(new_api_key: str):
    """更新数据库中的API密钥"""
    app = create_app()
    with app.app_context():
        try:
            # 加密新密钥
            print(f"🔐 正在加密新的API密钥...")
            encrypted_key = encryption_service.encrypt(new_api_key)

            # 更新数据库
            print(f"💾 正在更新数据库...")
            config_repo = APIConfigRepository()

            # 获取激活的配置ID
            active_config = config_repo.get_active()
            if not active_config:
                print("❌ 没有找到激活的配置")
                return False

            config_id = active_config['id']
            config_repo.update(config_id, openai_hk_api_key_encrypted=encrypted_key)

            print(f"✅ API密钥更新成功！配置ID: {config_id}")

            # 验证解密
            print(f"🔓 验证解密...")
            decrypted = encryption_service.decrypt(encrypted_key)
            if decrypted == new_api_key:
                print(f"✅ 解密验证成功！")
                print(f"📝 新密钥: {new_api_key}")
                return True
            else:
                print(f"❌ 解密验证失败！")
                return False

        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ 用法错误！")
        print("使用方法: python3 update_api_key.py YOUR_NEW_API_KEY")
        print("\n示例:")
        print("  python3 update_api_key.py hk-xxxxxxxxxxxxx")
        sys.exit(1)

    new_key = sys.argv[1]

    if not new_key.startswith('hk-'):
        print("⚠️  警告: API密钥通常以 'hk-' 开头")
        confirm = input("确定继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("❌ 已取消")
            sys.exit(0)

    if len(new_key) < 20:
        print("⚠️  警告: API密钥长度似乎太短")
        confirm = input("确定继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("❌ 已取消")
            sys.exit(0)

    success = update_api_key(new_key)
    sys.exit(0 if success else 1)
