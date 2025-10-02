#!/usr/bin/env python3
"""
Initialize Default API Configuration
====================================

This script creates a default API configuration group with encrypted API key.
"""

import os
import sys
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.encryption_service import encryption_service


def init_default_config():
    """Initialize default API configuration."""

    # Configuration values
    config_name = "Default Configuration"
    config_desc = "Default nano-banana API configuration"
    base_url = "https://api.openai-hk.com"
    # Replace with your actual API key
    api_key = "hk-vn7gna1000cc2bec0f3c59e6ab2c66b39fecef3d0fee3e10"

    # Encrypt API key
    try:
        encrypted_key = encryption_service.encrypt(api_key)
        print(f"✅ API密钥加密成功")
    except Exception as e:
        print(f"❌ 加密失败: {e}")
        return False

    # Connect to database
    db_path = Path(__file__).parent / "instance" / "database.db"
    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
        return False

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if config already exists
        cursor.execute("SELECT COUNT(*) FROM api_config_groups WHERE name = ?", (config_name,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"ℹ️  配置已存在: {config_name}")
            # Update existing config
            cursor.execute("""
                UPDATE api_config_groups
                SET openai_hk_base_url = ?,
                    openai_hk_api_key_encrypted = ?,
                    is_active = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (base_url, encrypted_key, config_name))
            print(f"✅ 已更新配置: {config_name}")
        else:
            # Deactivate all existing configs first
            cursor.execute("UPDATE api_config_groups SET is_active = 0")

            # Insert new config
            cursor.execute("""
                INSERT INTO api_config_groups
                (name, description, openai_hk_base_url, openai_hk_api_key_encrypted, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (config_name, config_desc, base_url, encrypted_key))
            print(f"✅ 已创建新配置: {config_name}")

        conn.commit()

        # Verify
        cursor.execute("""
            SELECT id, name, is_active, openai_hk_base_url
            FROM api_config_groups
            WHERE name = ?
        """, (config_name,))

        result = cursor.fetchone()
        if result:
            print(f"\n📊 配置详情:")
            print(f"  ID: {result[0]}")
            print(f"  Name: {result[1]}")
            print(f"  Active: {'✅' if result[2] else '❌'}")
            print(f"  Base URL: {result[3]}")
            print(f"\n✅ API配置初始化成功！")
            return True
        else:
            print("❌ 无法验证配置")
            return False

    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 开始初始化API配置...\n")
    success = init_default_config()
    sys.exit(0 if success else 1)
