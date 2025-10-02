"""
权限验证工具模块
提供装饰器和辅助函数用于权限控制
"""
from functools import wraps
from flask import g, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.database import get_db
from app.utils.response import APIResponse


def get_user_roles(user_id: int) -> list:
    """
    获取用户的所有角色

    Args:
        user_id: 用户ID

    Returns:
        角色列表，每个角色包含 id, name, display_name
    """
    db = get_db()
    roles = db.execute('''
        SELECT r.id, r.name, r.display_name, r.description
        FROM roles r
        JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = ?
    ''', (user_id,)).fetchall()

    return [dict(row) for row in roles]


def get_user_permissions(user_id: int) -> set:
    """
    获取用户的所有权限标识

    Args:
        user_id: 用户ID

    Returns:
        权限标识集合，例如 {'user.view', 'generation.create'}
    """
    db = get_db()
    permissions = db.execute('''
        SELECT DISTINCT p.name
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN user_roles ur ON rp.role_id = ur.role_id
        WHERE ur.user_id = ?
    ''', (user_id,)).fetchall()

    return {row['name'] for row in permissions}


def has_role(user_id: int, role_name: str) -> bool:
    """
    检查用户是否拥有指定角色

    Args:
        user_id: 用户ID
        role_name: 角色名称（如 'admin', 'user'）

    Returns:
        True表示拥有该角色，False表示没有
    """
    db = get_db()
    result = db.execute('''
        SELECT 1
        FROM user_roles ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = ? AND r.name = ?
        LIMIT 1
    ''', (user_id, role_name)).fetchone()

    return result is not None


def has_permission(user_id: int, permission_name: str) -> bool:
    """
    检查用户是否拥有指定权限

    Args:
        user_id: 用户ID
        permission_name: 权限标识（如 'user.create', 'config.edit'）

    Returns:
        True表示拥有该权限，False表示没有
    """
    permissions = get_user_permissions(user_id)
    return permission_name in permissions


def require_role(*role_names):
    """
    装饰器：要求用户拥有指定角色之一

    用法:
        @require_role('admin')
        def admin_only_endpoint():
            ...

        @require_role('admin', 'editor')
        def editor_or_admin_endpoint():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            # 检查用户是否拥有任一指定角色
            for role_name in role_names:
                if has_role(user_id, role_name):
                    return fn(*args, **kwargs)

            # 没有任何所需角色
            current_app.logger.warning(
                f"用户 {user_id} 尝试访问需要角色 {role_names} 的接口但被拒绝"
            )
            return APIResponse.forbidden(
                message="您没有权限访问此功能",
                error_code="INSUFFICIENT_ROLE"
            )

        return wrapper
    return decorator


def require_permission(*permission_names):
    """
    装饰器：要求用户拥有指定权限之一

    用法:
        @require_permission('user.create')
        def create_user_endpoint():
            ...

        @require_permission('config.edit', 'config.view')
        def config_endpoint():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            # 检查用户是否拥有任一指定权限
            user_permissions = get_user_permissions(user_id)
            for permission_name in permission_names:
                if permission_name in user_permissions:
                    return fn(*args, **kwargs)

            # 没有任何所需权限
            current_app.logger.warning(
                f"用户 {user_id} 尝试访问需要权限 {permission_names} 的接口但被拒绝"
            )
            return APIResponse.forbidden(
                message="您没有权限执行此操作",
                error_code="INSUFFICIENT_PERMISSION"
            )

        return wrapper
    return decorator


def require_all_permissions(*permission_names):
    """
    装饰器：要求用户拥有所有指定权限

    用法:
        @require_all_permissions('user.view', 'user.edit')
        def edit_user_endpoint():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            # 检查用户是否拥有所有指定权限
            user_permissions = get_user_permissions(user_id)
            missing_permissions = [
                p for p in permission_names if p not in user_permissions
            ]

            if missing_permissions:
                current_app.logger.warning(
                    f"用户 {user_id} 缺少权限 {missing_permissions}"
                )
                return APIResponse.forbidden(
                    message="您没有足够的权限执行此操作",
                    error_code="INSUFFICIENT_PERMISSION",
                    details={'missing_permissions': missing_permissions}
                )

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def load_user_context():
    """
    加载用户上下文信息到Flask g对象
    包括角色和权限信息

    在请求处理前调用，方便后续使用
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()

        if user_id:
            g.user_id = user_id
            g.user_roles = get_user_roles(user_id)
            g.user_permissions = get_user_permissions(user_id)
        else:
            g.user_id = None
            g.user_roles = []
            g.user_permissions = set()
    except Exception:
        g.user_id = None
        g.user_roles = []
        g.user_permissions = set()


def get_current_user_roles() -> list:
    """获取当前用户的角色列表"""
    return getattr(g, 'user_roles', [])


def get_current_user_permissions() -> set:
    """获取当前用户的权限集合"""
    return getattr(g, 'user_permissions', set())


def current_user_has_role(role_name: str) -> bool:
    """检查当前用户是否拥有指定角色"""
    roles = get_current_user_roles()
    return any(role['name'] == role_name for role in roles)


def current_user_has_permission(permission_name: str) -> bool:
    """检查当前用户是否拥有指定权限"""
    permissions = get_current_user_permissions()
    return permission_name in permissions