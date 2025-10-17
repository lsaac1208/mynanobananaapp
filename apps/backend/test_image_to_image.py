#!/usr/bin/env python3
"""
图生图API测试脚本
测试多图上传功能和官方API规范符合性
"""
import os
import sys
import requests

# 设置环境变量
os.environ['ENCRYPTION_MASTER_KEY'] = 'i3N5RYqusUuKU7Orhq8AxOBDYWoIkqF7pyqPIFBncMA='
os.environ['ENCRYPTION_SALT'] = '0CmHxpsIU9m3Arky1_V4V390xoz0VZ8XWdzfOMn_3n8='

def test_single_image():
    """测试单图上传（向后兼容）"""
    print("\n=== 测试1: 单图上传（向后兼容） ===")
    
    url = "http://localhost:5000/api/generate/image-to-image"
    
    # 请替换为您的实际 token
    token = input("请输入您的访问令牌 (access_token): ")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建一个测试图片文件（您需要提供实际的测试图片）
    test_image_path = input("请输入测试图片路径 (如: test1.png): ")
    
    if not os.path.exists(test_image_path):
        print(f"❌ 错误: 文件 {test_image_path} 不存在")
        return False
    
    with open(test_image_path, 'rb') as f:
        files = {
            'images[]': (os.path.basename(test_image_path), f, 'image/png')
        }
        
        data = {
            'prompt': 'a beautiful sunset landscape',
            'model': 'nano-banana'
        }
        
        print(f"📤 发送请求: {url}")
        print(f"📝 Prompt: {data['prompt']}")
        print(f"🖼️ 图片: {test_image_path}")
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 单图上传测试成功!")
                    print(f"🎨 生成图片数量: {len(result.get('images', []))}")
                    print(f"⏱️ 生成耗时: {result.get('generation_time')}秒")
                    return True
                else:
                    print(f"❌ 生成失败: {result.get('error')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            return False

def test_multiple_images():
    """测试多图上传（最多4张）"""
    print("\n=== 测试2: 多图上传 ===")
    
    url = "http://localhost:5000/api/generate/image-to-image"
    
    token = input("请输入您的访问令牌 (access_token): ")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取多个测试图片
    num_images = int(input("请输入要上传的图片数量 (1-4): "))
    
    if num_images < 1 or num_images > 4:
        print("❌ 图片数量必须在1-4之间")
        return False
    
    image_paths = []
    for i in range(num_images):
        path = input(f"请输入第 {i+1} 张图片的路径: ")
        if not os.path.exists(path):
            print(f"❌ 错误: 文件 {path} 不存在")
            return False
        image_paths.append(path)
    
    # 构建 multipart 请求
    files = []
    for path in image_paths:
        with open(path, 'rb') as f:
            files.append(
                ('images[]', (os.path.basename(path), f.read(), 'image/png'))
            )
    
    data = {
        'prompt': 'combine these images into a beautiful collage',
        'model': 'nano-banana'
    }
    
    print(f"📤 发送请求: {url}")
    print(f"📝 Prompt: {data['prompt']}")
    print(f"🖼️ 图片数量: {len(files)}")
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 多图上传测试成功!")
                print(f"🎨 生成图片数量: {len(result.get('images', []))}")
                print(f"⏱️ 生成耗时: {result.get('generation_time')}秒")
                return True
            else:
                print(f"❌ 生成失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_exceeding_limit():
    """测试超过4张图片的限制"""
    print("\n=== 测试3: 超过图片数量限制 ===")
    
    url = "http://localhost:5000/api/generate/image-to-image"
    
    token = input("请输入您的访问令牌 (access_token): ")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 模拟5张图片（应该被拒绝）
    print("ℹ️ 注意: 此测试预期会失败（超过4张限制）")
    
    test_image_path = input("请输入一张测试图片路径: ")
    
    if not os.path.exists(test_image_path):
        print(f"❌ 错误: 文件 {test_image_path} 不存在")
        return False
    
    with open(test_image_path, 'rb') as f:
        image_content = f.read()
    
    # 上传5张相同的图片
    files = [('images[]', (f'test{i}.png', image_content, 'image/png')) for i in range(5)]
    
    data = {
        'prompt': 'test prompt',
        'model': 'nano-banana'
    }
    
    print(f"📤 发送请求: {url} (包含5张图片)")
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            if 'Maximum 4 images allowed' in str(result.get('error', '')):
                print("✅ 超限测试成功! 系统正确拒绝了超过4张的请求")
                return True
            else:
                print(f"⚠️ 收到400错误，但错误消息不符: {result.get('error')}")
                return False
        else:
            print(f"❌ 预期返回400，但实际返回: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("图生图API规范化测试")
    print("=" * 60)
    
    # 检查后端是否运行
    try:
        response = requests.get("http://localhost:5000/api/check-token", timeout=5)
        print("✅ 后端服务已启动")
    except Exception as e:
        print("❌ 错误: 后端服务未启动或无法连接")
        print(f"   {str(e)}")
        print("\n请先运行后端服务:")
        print("   cd apps/backend && python3 app.py")
        return
    
    # 运行测试
    results = []
    
    print("\n请选择要运行的测试:")
    print("1. 单图上传测试")
    print("2. 多图上传测试")
    print("3. 超限测试")
    print("4. 运行所有测试")
    
    choice = input("\n请输入选项 (1-4): ")
    
    if choice == '1':
        results.append(("单图上传", test_single_image()))
    elif choice == '2':
        results.append(("多图上传", test_multiple_images()))
    elif choice == '3':
        results.append(("超限测试", test_exceeding_limit()))
    elif choice == '4':
        results.append(("单图上传", test_single_image()))
        results.append(("多图上传", test_multiple_images()))
        results.append(("超限测试", test_exceeding_limit()))
    else:
        print("❌ 无效选项")
        return
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！图生图API规范化修复成功！")
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查相关问题")

if __name__ == '__main__':
    main()

