"""
Flask应用工厂模块
"""
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import config

# 扩展实例
jwt = JWTManager()
cors = CORS()


def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    jwt.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])

    # 初始化数据库
    from app.database import init_app
    init_app(app)

    # 初始化性能日志中间件
    from app.middleware.performance_logger import PerformanceLogger
    PerformanceLogger.init_app(app)

    # JWT配置
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """检查JWT是否被撤销"""
        from app.database import JWTBlacklist
        jti = jwt_payload['jti']
        return JWTBlacklist.is_blacklisted(jti)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """令牌过期回调"""
        return {'error': '令牌已过期'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """无效令牌回调"""
        return {'error': '无效的令牌'}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """缺少令牌回调"""
        return {'error': '需要认证令牌'}, 401

    # 注册蓝图
    from app.views.auth import auth_bp
    from app.views.user import user_bp
    from app.views.generate import generate_bp
    from app.views.admin import admin_bp
    from app.views.config_groups import config_groups_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(generate_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(config_groups_bp, url_prefix='/api')

    # 注册CLI命令
    @app.cli.command()
    def init_db():
        """初始化数据库"""
        from app.database import init_db as _init_db
        _init_db()
        print('数据库已初始化')

    # 健康检查端点
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Nano-Banana API is running'}

    return app