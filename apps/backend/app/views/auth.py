"""
认证相关视图
"""
import re
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.middleware.rate_limiter import rate_limit

auth_bp = Blueprint('auth', __name__)

# 邮箱格式验证正则
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# 登录失败计数器（防暴力破解）
login_attempts = {}
LOGIN_ATTEMPT_LIMIT = 5
LOGIN_COOLDOWN_SECONDS = 300  # 5分钟冷却期


def validate_email(email):
    """验证邮箱格式"""
    return EMAIL_REGEX.match(email) is not None


def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码至少需要8个字符"

    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母"

    if not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母"

    if not re.search(r'[0-9]', password):
        return False, "密码必须包含至少一个数字"

    return True, "密码符合要求"


def check_login_attempts(email):
    """检查登录尝试次数"""
    now = time.time()
    if email in login_attempts:
        attempts, last_attempt = login_attempts[email]
        if attempts >= LOGIN_ATTEMPT_LIMIT:
            if now - last_attempt < LOGIN_COOLDOWN_SECONDS:
                return False, f"登录尝试过多，请在{int(LOGIN_COOLDOWN_SECONDS - (now - last_attempt))}秒后重试"
            else:
                # 冷却期已过，重置计数
                login_attempts[email] = (0, now)
    return True, ""


def record_login_attempt(email, success):
    """记录登录尝试"""
    now = time.time()
    if success:
        # 登录成功，清除记录
        login_attempts.pop(email, None)
    else:
        # 登录失败，增加计数
        attempts, _ = login_attempts.get(email, (0, now))
        login_attempts[email] = (attempts + 1, now)


@auth_bp.route('/register', methods=['POST'])
@rate_limit('register')
def register():
    """用户注册"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # 验证邮箱
        if not email:
            return jsonify({'error': '邮箱不能为空'}), 400

        if not validate_email(email):
            return jsonify({'error': '邮箱格式不正确'}), 400

        # 验证密码
        if not password:
            return jsonify({'error': '密码不能为空'}), 400

        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400

        # 创建用户
        from app.database import User
        user_id = User.create(email, password)

        if user_id is None:
            return jsonify({'error': '邮箱已被注册'}), 409

        # 生成JWT令牌（identity必须是字符串）
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))

        # 获取用户信息和角色
        user = User.get_by_id(user_id)
        from app.utils.permissions import get_user_roles
        roles = get_user_roles(user_id)

        # 创建用户会话记录
        try:
            from app.database import UserSession
            user_agent = request.headers.get('User-Agent', 'Unknown')
            ip_address = request.remote_addr
            UserSession.create_session(user_id, user_agent, ip_address)
        except Exception as session_error:
            current_app.logger.warning(f"创建用户会话记录失败: {str(session_error)}")

        return jsonify({
            'message': '注册成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'credits': user['credits'],
                'is_active': user['is_active'],
                'created_at': user['created_at'],
                'last_login_at': user.get('last_login_at'),
                'updated_at': user.get('updated_at'),
                'roles': roles
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"注册失败: {str(e)}")
        return jsonify({'error': '注册失败，请稍后重试'}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit('login')
def login():
    """用户登录"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # 基本验证
        if not email or not password:
            return jsonify({'error': '邮箱和密码不能为空'}), 400

        # 检查登录尝试次数
        can_attempt, error_msg = check_login_attempts(email)
        if not can_attempt:
            return jsonify({'error': error_msg}), 429

        # 获取用户
        from app.database import User
        user = User.get_by_email(email)

        if not user:
            record_login_attempt(email, False)
            return jsonify({'error': '邮箱或密码错误'}), 401

        # 检查用户是否被锁定
        if User.is_locked(user):
            return jsonify({'error': '账户已被锁定，请稍后重试'}), 403

        # 验证密码
        if not User.verify_password(user, password):
            record_login_attempt(email, False)
            User.update_login_info(user['id'], success=False)
            return jsonify({'error': '邮箱或密码错误'}), 401

        # 检查账户状态
        if not user['is_active']:
            return jsonify({'error': '账户已被禁用'}), 403

        # 登录成功
        record_login_attempt(email, True)
        User.update_login_info(user['id'], success=True)

        # 生成JWT令牌（identity必须是字符串）
        access_token = create_access_token(identity=str(user['id']))
        refresh_token = create_refresh_token(identity=str(user['id']))

        # 获取用户角色
        from app.utils.permissions import get_user_roles
        roles = get_user_roles(user['id'])

        # 创建用户会话记录
        try:
            from app.database import UserSession
            user_agent = request.headers.get('User-Agent', 'Unknown')
            ip_address = request.remote_addr
            UserSession.create_session(user['id'], user_agent, ip_address)
        except Exception as session_error:
            current_app.logger.warning(f"创建用户会话记录失败: {str(session_error)}")

        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'credits': user['credits'],
                'is_active': user['is_active'],
                'created_at': user['created_at'],
                'last_login_at': user.get('last_login_at'),
                'updated_at': user.get('updated_at'),
                'roles': roles
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"登录失败: {str(e)}")
        return jsonify({'error': '登录失败，请稍后重试'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        # 获取当前JWT的JTI
        jti = get_jwt()['jti']

        # 添加到黑名单
        from app.database import JWTBlacklist
        JWTBlacklist.add(jti)

        return jsonify({'message': '登出成功'}), 200

    except Exception as e:
        current_app.logger.error(f"登出失败: {str(e)}")
        return jsonify({'error': '登出失败'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = int(get_jwt_identity())

        # 检查用户是否仍然存在且激活
        from app.database import User
        user = User.get_by_id(current_user_id)

        if not user or not user['is_active']:
            return jsonify({'error': '用户不存在或已被禁用'}), 401

        # 生成新的访问令牌（identity必须是字符串）
        new_access_token = create_access_token(identity=str(current_user_id))

        return jsonify({
            'access_token': new_access_token
        }), 200

    except Exception as e:
        current_app.logger.error(f"令牌刷新失败: {str(e)}")
        return jsonify({'error': '令牌刷新失败'}), 500


@auth_bp.route('/check-token', methods=['GET'])
@jwt_required()
def check_token():
    """检查令牌有效性"""
    try:
        current_user_id = int(get_jwt_identity())

        # 获取用户信息
        from app.database import User
        user = User.get_by_id(current_user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        if not user['is_active']:
            return jsonify({'error': '用户已被禁用'}), 403

        # 获取用户角色
        from app.utils.permissions import get_user_roles
        roles = get_user_roles(user['id'])

        return jsonify({
            'message': '令牌有效',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'credits': user['credits'],
                'is_active': user['is_active'],
                'created_at': user['created_at'],
                'last_login_at': user.get('last_login_at'),
                'updated_at': user.get('updated_at'),
                'roles': roles
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"令牌检查失败: {str(e)}")
        return jsonify({'error': '令牌检查失败'}), 500


@auth_bp.route('/me/permissions', methods=['GET'])
@jwt_required()
def get_my_permissions():
    """获取当前用户的权限列表"""
    try:
        current_user_id = int(get_jwt_identity())

        # 获取用户信息
        from app.database import User
        user = User.get_by_id(current_user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        if not user['is_active']:
            return jsonify({'error': '用户已被禁用'}), 403

        # 获取用户角色和权限
        from app.utils.permissions import get_user_roles, get_user_permissions
        roles = get_user_roles(current_user_id)
        permissions = list(get_user_permissions(current_user_id))

        return jsonify({
            'roles': roles,
            'permissions': permissions
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取权限失败: {str(e)}")
        return jsonify({'error': '获取权限失败'}), 500


@auth_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_all_roles():
    """获取所有角色列表（仅管理员）"""
    try:
        current_user_id = int(get_jwt_identity())

        # 检查管理员权限
        from app.utils.permissions import has_role
        if not has_role(current_user_id, 'admin'):
            return jsonify({'error': '需要管理员权限'}), 403

        # 获取所有角色
        from app.database import get_db
        db = get_db()
        roles = db.execute('''
            SELECT id, name, display_name, description, is_system, created_at, updated_at
            FROM roles
            ORDER BY name
        ''').fetchall()

        return jsonify({
            'roles': [dict(row) for row in roles]
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取角色列表失败: {str(e)}")
        return jsonify({'error': '获取角色列表失败'}), 500