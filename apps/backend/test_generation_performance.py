#!/usr/bin/env python3
"""
性能测试脚本 - 测试文生图和图生图的性能
"""
import sys
import time
import requests
from pathlib import Path

# 添加app目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "email": "test999@example.com",
    "password": "Test123456!"
}

def login():
    """登录获取token"""
    print("🔐 登录测试用户...")
    response = requests.post(
        f"{BASE_URL}/api/login",
        json=TEST_USER
    )

    if response.status_code == 200:
        data = response.json()
        token = data['data']['access_token']
        print(f"✅ 登录成功 - Token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        sys.exit(1)

def test_text_to_image(token, model="nano-banana"):
    """测试文生图性能"""
    print(f"\n{'='*60}")
    print(f"📊 测试文生图性能 - 模型: {model}")
    print(f"{'='*60}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": "a cute orange cat playing in a garden with colorful flowers",
        "model": model,
        "size": "1x1",
        "n": 1
    }

    print(f"📝 提示词: {payload['prompt']}")
    print(f"🎨 模型: {payload['model']}")
    print(f"📐 尺寸: {payload['size']}")

    start_time = time.time()
    print(f"⏰ 开始时间: {time.strftime('%H:%M:%S')}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/generate/text-to-image",
            headers=headers,
            json=payload,
            timeout=120  # 2分钟超时
        )

        elapsed = time.time() - start_time

        print(f"⏱️ 请求耗时: {elapsed:.2f}秒")
        print(f"📡 HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ 生成成功!")
                print(f"   - 生成耗时: {data['data'].get('generation_time', 'N/A')}秒")
                print(f"   - 图片URL: {data['data']['images'][0]['url'][:80]}...")
                return True, elapsed
            else:
                print(f"❌ 生成失败: {data.get('message', 'Unknown error')}")
                return False, elapsed
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return False, elapsed

    except requests.Timeout:
        elapsed = time.time() - start_time
        print(f"⏱️ 请求超时 (>{elapsed:.2f}秒)")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 请求异常: {str(e)}")
        return False, elapsed

def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("🧪 nano-banana AI生成性能测试")
    print("="*60)

    # 登录
    token = login()

    # 测试普通模型
    print("\n" + "="*60)
    print("测试1: 普通模型 (nano-banana)")
    print("="*60)
    success1, time1 = test_text_to_image(token, "nano-banana")

    # 等待一下
    print("\n⏳ 等待5秒...")
    time.sleep(5)

    # 测试HD模型
    print("\n" + "="*60)
    print("测试2: HD模型 (nano-banana-hd)")
    print("="*60)
    success2, time2 = test_text_to_image(token, "nano-banana-hd")

    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"普通模型: {'✅ 成功' if success1 else '❌ 失败'} - {time1:.2f}秒")
    print(f"HD模型:   {'✅ 成功' if success2 else '❌ 失败'} - {time2:.2f}秒")

    if success1 and success2:
        print(f"\n💡 速度差异: HD模型比普通模型慢 {time2 - time1:.2f}秒 ({((time2/time1 - 1) * 100):.1f}%)")

    print("\n" + "="*60)
    print("提示: 查看后端日志了解详细性能分析")
    print("="*60)

if __name__ == "__main__":
    main()
