#!/usr/bin/env python3
"""
修复API配置的Base URL
"""
import os
import sys
os.environ['ENCRYPTION_MASTER_KEY'] = 'i3N5RYqusUuKU7Orhq8AxOBDYWoIkqF7pyqPIFBncMA='
os.environ['ENCRYPTION_SALT'] = '0CmHxpsIU9m3Arky1_V4V390xoz0VZ8XWdzfOMn_3n8='

from app import create_app
from app.database import get_db

app = create_app()

with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取当前配置
    cursor.execute("SELECT id, name, openai_hk_base_url FROM api_config_groups WHERE id = 2")
    config = cursor.fetchone()
    
    if config:
        config_id, name, old_url = config
        print(f"当前配置:")
        print(f"  ID: {config_id}")
        print(f"  名称: {name}")
        print(f"  旧URL: {old_url}")
        print()
        
        # 修复URL
        new_url = "https://api.openai-hk.com"
        
        print(f"修复为:")
        print(f"  新URL: {new_url}")
        print()
        
        # 更新数据库
        cursor.execute(
            "UPDATE api_config_groups SET openai_hk_base_url = ? WHERE id = ?",
            (new_url, config_id)
        )
        conn.commit()
        
        print("✅ API配置已更新！")
        print()
        print("说明:")
        print("  Base URL应该只包含域名部分: https://api.openai-hk.com")
        print("  具体的endpoint路径（如/v1/images）会在调用时自动添加")
    else:
        print("❌ 未找到ID为2的配置")

