#!/usr/bin/env python3
"""
修复API密钥问题
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import create_app
from app.services.encryption_service import encryption_service
from app.repositories.api_config_repository import APIConfigRepository

# 正确的API密钥
CORRECT_API_KEY = "hk-z3pube100001739337bad3455bc8f18e6c1dfb50bfe5e8e3"

app = create_app()
with app.app_context():
    try:
        print("=" * 70)
        print("🔧 修复API密钥")
        print("=" * 70)

        config_repo = APIConfigRepository()

        # 获取激活的配置
        active_config = config_repo.get_active()
        if not active_config:
            print("❌ 没有找到激活的配置")
            exit(1)

        print(f"\n📋 当前配置:")
        print(f"   ID: {active_config['id']}")
        print(f"   Name: {active_config['name']}")

        # 检查当前存储的密钥
        try:
            current_key = encryption_service.decrypt(active_config['openai_hk_api_key_encrypted'])
            print(f"\n🔍 当前解密的密钥:")
            print(f"   密钥: {current_key}")
            print(f"   长度: {len(current_key)}")

            if current_key == CORRECT_API_KEY:
                print(f"\n✅ 密钥已经正确! 无需更新")
                exit(0)
            else:
                print(f"\n⚠️  密钥不正确，需要更新")
                print(f"   当前: {current_key[:20]}...")
                print(f"   正确: {CORRECT_API_KEY[:20]}...")

        except Exception as e:
            print(f"\n❌ 解密当前密钥失败: {str(e)}")

        # 加密正确的密钥
        print(f"\n🔐 加密正确的密钥...")
        new_encrypted = encryption_service.encrypt(CORRECT_API_KEY)
        print(f"✅ 加密成功")

        # 验证加密结果
        print(f"\n🔓 验证加密结果...")
        test_decrypt = encryption_service.decrypt(new_encrypted)
        if test_decrypt == CORRECT_API_KEY:
            print(f"✅ 验证成功: {test_decrypt}")
        else:
            print(f"❌ 验证失败!")
            print(f"   期望: {CORRECT_API_KEY}")
            print(f"   实际: {test_decrypt}")
            exit(1)

        # 更新到数据库
        print(f"\n💾 更新数据库...")
        config_repo.update(active_config['id'], openai_hk_api_key_encrypted=new_encrypted)
        print(f"✅ 数据库更新成功!")

        # 最终验证
        print(f"\n🔍 最终验证...")
        final_config = config_repo.get_active()
        final_key = encryption_service.decrypt(final_config['openai_hk_api_key_encrypted'])

        if final_key == CORRECT_API_KEY:
            print(f"\n" + "=" * 70)
            print(f"✅✅✅ API密钥修复成功!")
            print(f"=" * 70)
            print(f"\n密钥: {final_key}")
            print(f"\n🔄 请重启后端服务以应用更改")
        else:
            print(f"\n❌ 最终验证失败")
            print(f"   期望: {CORRECT_API_KEY}")
            print(f"   实际: {final_key}")
            exit(1)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
