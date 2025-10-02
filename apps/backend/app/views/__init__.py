"""
视图蓝图模块
"""
from .auth import auth_bp
from .user import user_bp
from .generate import generate_bp
from .gallery import gallery_bp
from .admin import admin_bp

__all__ = ['auth_bp', 'user_bp', 'generate_bp', 'gallery_bp', 'admin_bp']