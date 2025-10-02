"""
用户数据模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """用户模型"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    credits = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    creations = db.relationship('Creation', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def add_credits(self, amount):
        """增加次数"""
        if amount > 0:
            self.credits += amount
            self.updated_at = datetime.utcnow()
            db.session.commit()

    def consume_credit(self):
        """消费一次"""
        if self.credits > 0:
            self.credits -= 1
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def deactivate(self):
        """停用用户账号"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def activate(self):
        """激活用户账号"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """转换为字典（不包含敏感信息）"""
        return {
            'id': self.id,
            'email': self.email,
            'credits': self.credits,
            'is_active': self.is_active,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.email}>'