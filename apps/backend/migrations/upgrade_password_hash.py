"""
密码哈希升级迁移脚本
从 SHA256 升级到 pbkdf2:sha256

运行方式：
    python apps/backend/migrations/upgrade_password_hash.py
"""
import sqlite3
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from werkzeug.security import generate_password_hash


def get_db_path():
    """获取数据库文件路径"""
    # 使用实例目录的数据库
    instance_path = project_root / 'apps' / 'backend' / 'instance'
    return instance_path / 'database.db'


def migrate_password_hashes():
    """
    迁移现有用户的密码哈希格式
    
    注意：由于旧的 SHA256 哈希是单向的，无法直接转换为新格式。
    解决方案：
    1. 自动升级策略：用户下次成功登录时，系统会自动将其密码升级到新格式
    2. 管理员可以选择重置所有用户密码（可选，仅在必要时使用）
    
    本脚本主要用于：
    - 统计当前使用旧格式的用户数量
    - 提供批量密码重置选项（仅在确实需要时）
    """
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"📁 数据库路径: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 统计用户数量
        total_users = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        print(f"\n📊 总用户数: {total_users}")
        
        if total_users == 0:
            print("✅ 没有用户需要迁移")
            return
        
        # 统计旧格式密码的用户（SHA256哈希长度为64个字符）
        old_format_users = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE length(password_hash) = 64"
        ).fetchone()[0]
        
        new_format_users = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE password_hash LIKE 'pbkdf2:sha256:%'"
        ).fetchone()[0]
        
        print(f"📈 使用旧格式 (SHA256) 的用户: {old_format_users}")
        print(f"✅ 使用新格式 (pbkdf2:sha256) 的用户: {new_format_users}")
        
        if old_format_users == 0:
            print("\n🎉 所有用户已使用新格式密码！")
            return
        
        print(f"\n⚠️  检测到 {old_format_users} 个用户仍在使用旧格式密码")
        print("\n自动升级策略：")
        print("  - 用户下次成功登录时，密码会自动升级到新格式")
        print("  - 无需手动干预")
        print("  - 升级过程对用户透明")
        
        # 可选：批量重置密码（仅在必要时使用）
        print("\n" + "="*60)
        print("可选操作：批量密码重置")
        print("="*60)
        print("⚠️  警告：此操作会将所有旧格式用户的密码重置为临时密码")
        print("   用户需要使用临时密码登录后重新设置密码")
        print("\n是否执行批量重置？(yes/no)")
        
        choice = input("请输入选择: ").strip().lower()
        
        if choice == 'yes':
            # 生成临时密码
            temp_password = "TempPass@2025"
            temp_hash = generate_password_hash(temp_password, method='pbkdf2:sha256')
            
            # 更新所有旧格式用户的密码
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE length(password_hash) = 64",
                (temp_hash,)
            )
            conn.commit()
            
            affected_rows = cursor.rowcount
            print(f"\n✅ 已重置 {affected_rows} 个用户的密码")
            print(f"📝 临时密码: {temp_password}")
            print("⚠️  请通知用户使用临时密码登录并立即更改密码！")
            
            # 保存通知信息到文件
            notification_file = project_root / 'PASSWORD_RESET_NOTICE.txt'
            with open(notification_file, 'w', encoding='utf-8') as f:
                f.write(f"密码重置通知\n")
                f.write(f"=" * 60 + "\n\n")
                f.write(f"临时密码: {temp_password}\n\n")
                f.write(f"受影响的用户数: {affected_rows}\n\n")
                f.write(f"请通知所有用户：\n")
                f.write(f"1. 使用临时密码登录\n")
                f.write(f"2. 立即在个人中心更改密码\n")
                f.write(f"3. 设置强密码（至少8位，包含大小写字母、数字和特殊字符）\n")
            
            print(f"📄 通知信息已保存到: {notification_file}")
        else:
            print("\n✅ 跳过批量重置，将使用自动升级策略")
        
        print("\n✨ 迁移检查完成！")
        
    except Exception as e:
        print(f"❌ 迁移过程中出错: {str(e)}")
        conn.rollback()
    finally:
        conn.close()


def verify_migration():
    """验证迁移结果"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查所有用户的密码格式
        old_format = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE length(password_hash) = 64"
        ).fetchone()[0]
        
        new_format = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE password_hash LIKE 'pbkdf2:sha256:%'"
        ).fetchone()[0]
        
        total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        
        print("\n" + "="*60)
        print("迁移验证结果")
        print("="*60)
        print(f"总用户数: {total}")
        print(f"新格式用户: {new_format} ({new_format/total*100 if total > 0 else 0:.1f}%)")
        print(f"旧格式用户: {old_format} ({old_format/total*100 if total > 0 else 0:.1f}%)")
        
        if old_format == 0 and total > 0:
            print("\n✅ 所有用户已成功迁移到新格式！")
        elif old_format > 0:
            print(f"\n⚠️  仍有 {old_format} 个用户使用旧格式")
            print("   这些用户将在下次登录时自动升级")
        
    except Exception as e:
        print(f"❌ 验证过程中出错: {str(e)}")
    finally:
        conn.close()


if __name__ == '__main__':
    print("="*60)
    print("密码哈希升级迁移工具")
    print("SHA256 → pbkdf2:sha256")
    print("="*60)
    
    migrate_password_hashes()
    verify_migration()
    
    print("\n" + "="*60)
    print("迁移完成")
    print("="*60)

