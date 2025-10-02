"""
认证系统测试脚本
"""
import requests
import json


def test_auth_system():
    """测试认证系统"""
    base_url = 'http://localhost:5000/api'

    print("🧪 开始测试认证系统...")

    # 测试数据
    test_user = {
        'email': 'test@example.com',
        'password': 'test123456'
    }

    print(f"\n📝 测试用户数据: {test_user['email']}")

    # 1. 测试用户注册
    print("\n1️⃣ 测试用户注册...")
    try:
        response = requests.post(f'{base_url}/register', json=test_user)
        if response.status_code == 201:
            data = response.json()
            print("✅ 注册成功")
            print(f"👤 用户ID: {data['user']['id']}")
            print(f"💰 初始次数: {data['user']['credits']}")
            access_token = data['access_token']
            refresh_token = data['refresh_token']
        else:
            print(f"❌ 注册失败: {response.json().get('error', 'Unknown error')}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        print("💡 提示: 请确保后端服务器正在运行 (npm run dev:backend)")
        return

    # 2. 测试重复注册
    print("\n2️⃣ 测试重复注册...")
    response = requests.post(f'{base_url}/register', json=test_user)
    if response.status_code == 400:
        print("✅ 正确拒绝重复注册")
    else:
        print("❌ 重复注册检查失败")

    # 3. 测试用户登录
    print("\n3️⃣ 测试用户登录...")
    response = requests.post(f'{base_url}/login', json=test_user)
    if response.status_code == 200:
        data = response.json()
        print("✅ 登录成功")
        login_access_token = data['access_token']
    else:
        print(f"❌ 登录失败: {response.json().get('error', 'Unknown error')}")
        return

    # 4. 测试错误密码登录
    print("\n4️⃣ 测试错误密码登录...")
    wrong_user = {**test_user, 'password': 'wrongpassword'}
    response = requests.post(f'{base_url}/login', json=wrong_user)
    if response.status_code == 401:
        print("✅ 正确拒绝错误密码")
    else:
        print("❌ 错误密码检查失败")

    # 5. 测试令牌验证
    print("\n5️⃣ 测试令牌验证...")
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{base_url}/check-token', headers=headers)
    if response.status_code == 200:
        print("✅ 令牌验证成功")
    else:
        print("❌ 令牌验证失败")

    # 6. 测试获取用户信息
    print("\n6️⃣ 测试获取用户信息...")
    response = requests.get(f'{base_url}/users/me', headers=headers)
    if response.status_code == 200:
        print("✅ 获取用户信息成功")
        user_data = response.json()['user']
        print(f"📧 邮箱: {user_data['email']}")
        print(f"💰 次数: {user_data['credits']}")
    else:
        print("❌ 获取用户信息失败")

    # 7. 测试令牌刷新
    print("\n7️⃣ 测试令牌刷新...")
    refresh_headers = {'Authorization': f'Bearer {refresh_token}'}
    response = requests.post(f'{base_url}/refresh', headers=refresh_headers)
    if response.status_code == 200:
        print("✅ 令牌刷新成功")
        new_access_token = response.json()['access_token']
    else:
        print("❌ 令牌刷新失败")

    # 8. 测试登出
    print("\n8️⃣ 测试登出...")
    response = requests.post(f'{base_url}/logout', headers=headers)
    if response.status_code == 200:
        print("✅ 登出成功")
    else:
        print("❌ 登出失败")

    # 9. 测试登出后的令牌访问
    print("\n9️⃣ 测试登出后的令牌访问...")
    response = requests.get(f'{base_url}/users/me', headers=headers)
    if response.status_code == 401:
        print("✅ 登出后令牌正确失效")
    else:
        print("❌ 登出后令牌仍然有效")

    print("\n🎉 认证系统测试完成！")


if __name__ == '__main__':
    test_auth_system()