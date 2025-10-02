"""
用户相关视图
"""
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__)


@user_bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    try:
        current_user_id = get_jwt_identity()

        # 获取用户信息
        from app.database import User
        user = User.get_by_id(current_user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'credits': user['credits'],
                'is_active': user['is_active'],
                'created_at': user['created_at'],
                'last_login_at': user['last_login_at']
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({'error': '获取用户信息失败'}), 500


@user_bp.route('/users/me/credits', methods=['GET'])
@jwt_required()
def get_user_credits():
    """获取用户次数"""
    try:
        current_user_id = get_jwt_identity()

        # 获取用户信息
        from app.database import User
        user = User.get_by_id(current_user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({
            'credits': user['credits']
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取用户次数失败: {str(e)}")
        return jsonify({'error': '获取用户次数失败'}), 500