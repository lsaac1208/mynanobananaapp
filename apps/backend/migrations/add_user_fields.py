"""
添加用户模型的新字段
增加: is_active, last_login_at 字段
"""
from app import create_app, db
from app.models import User

def upgrade():
    """升级数据库"""
    app = create_app()
    with app.app_context():
        try:
            # 检查字段是否已存在，避免重复添加
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]

            # 添加新字段（如果不存在）
            if 'is_active' not in columns:
                db.engine.execute('ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1')
                print("Added is_active column")

            if 'last_login_at' not in columns:
                db.engine.execute('ALTER TABLE users ADD COLUMN last_login_at DATETIME')
                print("Added last_login_at column")

            print("Database migration completed successfully")

        except Exception as e:
            print(f"Migration error: {e}")
            raise

def downgrade():
    """降级数据库"""
    app = create_app()
    with app.app_context():
        try:
            # 检查字段是否存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]

            # 移除字段（如果存在）
            if 'last_login_at' in columns:
                db.engine.execute('ALTER TABLE users DROP COLUMN last_login_at')
                print("Removed last_login_at column")

            if 'is_active' in columns:
                db.engine.execute('ALTER TABLE users DROP COLUMN is_active')
                print("Removed is_active column")

            print("Database downgrade completed successfully")

        except Exception as e:
            print(f"Downgrade error: {e}")
            raise

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()