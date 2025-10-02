"""
应用配置模块
"""
import os
from datetime import timedelta


class Config:
    """基础配置类"""

    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # JWT配置（安全优化：缩短有效期）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)  # 从24h缩短为2h
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # 外部API配置
    OPENAI_HK_API_KEY = os.environ.get('OPENAI_HK_API_KEY')
    OPENAI_HK_BASE_URL = 'https://api.openai-hk.com'

    # CORS配置（修复：支持前端实际端口）
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS',
        'http://localhost:3001,http://localhost:3000'
    ).split(',')

    # 上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

    # 开发环境API密钥（实际部署时应使用环境变量）
    OPENAI_HK_API_KEY = os.environ.get('OPENAI_HK_API_KEY') or 'hk-jtye3w10000173935031778c32c31864fe2fa87037f7d7f5'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False

    def __init__(self):
        """生产环境强制要求环境变量"""
        super().__init__()

        # 安全检查：生产环境必须设置这些环境变量
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'ENCRYPTION_KEY',
            'OPENAI_HK_API_KEY'
        ]

        missing_vars = [var for var in required_vars if not os.environ.get(var)]

        if missing_vars:
            raise EnvironmentError(
                f"生产环境缺少必需的环境变量: {', '.join(missing_vars)}\n"
                f"请设置这些环境变量后再启动应用"
            )


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}