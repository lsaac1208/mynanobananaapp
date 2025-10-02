"""
作品数据模型
"""
from datetime import datetime
from app import db


class Creation(db.Model):
    """作品模型"""

    __tablename__ = 'creations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    prompt = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    model_used = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __init__(self, user_id, prompt, image_url, model_used, size):
        self.user_id = user_id
        self.prompt = prompt
        self.image_url = image_url
        self.model_used = model_used
        self.size = size

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prompt': self.prompt,
            'image_url': self.image_url,
            'model_used': self.model_used,
            'size': self.size,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Creation {self.id} by User {self.user_id}>'