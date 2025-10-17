"""
应用数据库性能索引
执行 add_performance_indexes.sql 中定义的所有索引
"""
import sqlite3
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def get_db_path():
    """获取数据库文件路径"""
    instance_path = project_root / 'apps' / 'backend' / 'instance'
    return instance_path / 'database.db'


def apply_indexes():
    """应用所有性能索引"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"📁 数据库路径: {db_path}")
    print(f"📊 数据库大小: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # 读取SQL文件
    sql_file = Path(__file__).parent / 'add_performance_indexes.sql'
    if not sql_file.exists():
        print(f"❌ SQL文件不存在: {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("开始应用性能索引")
        print("="*60)
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行SQL（SQLite支持一次执行多个语句）
        cursor.executescript(sql_content)
        conn.commit()
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ 索引应用成功！")
        print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
        
        # 查询已创建的索引
        print("\n" + "="*60)
        print("已创建的索引列表")
        print("="*60)
        
        tables = [
            'creations',
            'performance_metrics', 
            'user_sessions',
            'user_behavior',
            'daily_stats',
            'jwt_blacklist',
            'users',
            'smart_recommendations',
            'system_settings'
        ]
        
        total_indexes = 0
        for table in tables:
            cursor.execute(f"PRAGMA index_list('{table}')")
            indexes = cursor.fetchall()
            
            if indexes:
                print(f"\n📋 {table}:")
                for idx in indexes:
                    index_name = idx['name']
                    if index_name.startswith('idx_'):  # 只显示我们创建的索引
                        print(f"  - {index_name}")
                        total_indexes += 1
        
        print(f"\n✨ 总计创建索引数: {total_indexes}")
        
        # 显示数据库大小变化
        new_size = db_path.stat().st_size / 1024 / 1024
        print(f"📊 优化后数据库大小: {new_size:.2f} MB")
        
        # 运行ANALYZE更新统计信息
        print("\n" + "="*60)
        print("更新查询优化器统计信息")
        print("="*60)
        cursor.execute("ANALYZE")
        conn.commit()
        print("✅ ANALYZE 完成")
        
        # 性能测试示例
        print("\n" + "="*60)
        print("性能测试示例")
        print("="*60)
        
        # 测试1: 用户作品查询
        test_query = """
            EXPLAIN QUERY PLAN 
            SELECT * FROM creations 
            WHERE user_id = 1 
            ORDER BY created_at DESC 
            LIMIT 20
        """
        cursor.execute(test_query)
        plan = cursor.fetchall()
        
        print("\n测试查询: 用户作品列表")
        for row in plan:
            detail = row[3] if len(row) > 3 else row
            print(f"  {detail}")
            if 'idx_creations_user_created' in str(detail):
                print("  ✅ 使用了索引！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 应用索引失败: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_indexes():
    """验证索引创建情况"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 统计所有以 idx_ 开头的索引
        cursor.execute("""
            SELECT name, tbl_name 
            FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
            ORDER BY tbl_name, name
        """)
        
        indexes = cursor.fetchall()
        
        print("\n" + "="*60)
        print("索引验证报告")
        print("="*60)
        
        if not indexes:
            print("⚠️  未找到任何性能索引")
            return False
        
        # 按表分组
        table_indexes = {}
        for name, table in indexes:
            if table not in table_indexes:
                table_indexes[table] = []
            table_indexes[table].append(name)
        
        for table, idx_list in sorted(table_indexes.items()):
            print(f"\n📋 {table} ({len(idx_list)} 个索引):")
            for idx_name in idx_list:
                print(f"  - {idx_name}")
        
        print(f"\n✅ 总计: {len(indexes)} 个性能索引")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False
    finally:
        conn.close()


def show_table_stats():
    """显示表的统计信息"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("表统计信息")
        print("="*60)
        
        tables = [
            'users',
            'creations',
            'performance_metrics',
            'user_sessions',
            'user_behavior',
            'daily_stats'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:25} {count:>10,} 行")
            except:
                pass
        
    finally:
        conn.close()


if __name__ == '__main__':
    print("="*60)
    print("数据库性能索引应用工具")
    print("="*60)
    
    # 显示表统计
    show_table_stats()
    
    # 应用索引
    success = apply_indexes()
    
    # 验证索引
    if success:
        verify_indexes()
        
        print("\n" + "="*60)
        print("✨ 索引应用完成！")
        print("="*60)
        print("\n建议:")
        print("1. 运行应用测试确保功能正常")
        print("2. 观察查询性能是否提升")
        print("3. 定期运行 ANALYZE 更新统计信息")
        print("4. 监控数据库文件大小")
    else:
        print("\n" + "="*60)
        print("❌ 索引应用失败")
        print("="*60)
        sys.exit(1)

