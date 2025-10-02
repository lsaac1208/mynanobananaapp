#!/usr/bin/env python3
"""
测试API密钥加密解密
"""
from app import create_app
from app.services.encryption_service import encryption_service
from app.repositories.api_config_repository import APIConfigRepository

app = create_app()
with app.app_context():
    try:
        print("=" * 60)
        print("🔍 检查API配置")
        print("=" * 60)

        config_repo = APIConfigRepository()

        # 获取激活的配置
        active_config = config_repo.get_active()
        if not active_config:
            print("❌ 没有找到激活的配置")
            exit(1)

        print(f"\n✅ 找到激活配置:")
        print(f"   ID: {active_config['id']}")
        print(f"   Name: {active_config['name']}")
        print(f"   Is Active: {active_config['is_active']}")

        # 检查加密密钥
        encrypted_key = active_config.get('openai_hk_api_key_encrypted')
        if not encrypted_key:
            print("\n❌ 没有存储的API密钥")
            exit(1)

        print(f"\n🔐 加密密钥信息:")
        print(f"   长度: {len(encrypted_key)} bytes")
        print(f"   前20字符: {encrypted_key[:20]}")

        # 尝试解密
        print(f"\n🔓 尝试解密...")
        try:
            decrypted_key = encryption_service.decrypt(encrypted_key)
            print(f"✅ 解密成功!")
            print(f"   解密后的密钥: {decrypted_key}")
            print(f"   密钥长度: {len(decrypted_key)}")
            print(f"   密钥前缀: {decrypted_key[:10] if len(decrypted_key) >= 10 else decrypted_key}")

            # 验证密钥格式
            if decrypted_key.startswith('hk-'):
                print(f"✅ 密钥格式正确 (以hk-开头)")
            else:
                print(f"⚠️  密钥格式异常 (不以hk-开头)")

        except Exception as decrypt_error:
            print(f"❌ 解密失败: {str(decrypt_error)}")
            import traceback
            traceback.print_exc()
            exit(1)

        # 现在测试用正确的密钥重新加密
        print(f"\n🔄 测试重新加密正确的密钥...")
        correct_key = "hk-z3pube100001739337bad3455bc8f18e6c1dfb50bfe5e8e3"

        try:
            new_encrypted = encryption_service.encrypt(correct_key)
            print(f"✅ 重新加密成功")
            print(f"   新加密密钥长度: {len(new_encrypted)}")

            # 测试解密新密钥
            test_decrypt = encryption_service.decrypt(new_encrypted)
            if test_decrypt == correct_key:
                print(f"✅ 新密钥解密验证成功")

                # 更新到数据库
                print(f"\n💾 更新数据库...")
                config_repo.update(active_config['id'], openai_hk_api_key_encrypted=new_encrypted)
                print(f"✅ 数据库更新成功!")

                # 再次验证
                print(f"\n🔍 验证更新后的配置...")
                updated_config = config_repo.get_active()
                final_decrypted = encryption_service.decrypt(updated_config['openai_hk_api_key_encrypted'])

                if final_decrypted == correct_key:
                    print(f"✅✅✅ 最终验证成功! API密钥已正确更新!")
                    print(f"   最终密钥: {final_decrypted}")
                else:
                    print(f"❌ 最终验证失败")
                    print(f"   期望: {correct_key}")
                    print(f"   实际: {final_decrypted}")
            else:
                print(f"❌ 新密钥解密验证失败")
                print(f"   期望: {correct_key}")
                print(f"   实际: {test_decrypt}")

        except Exception as e:
            print(f"❌ 重新加密过程失败: {str(e)}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
