"""
配置组管理相关视图
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import get_db
from app.utils.permissions import require_role
from cryptography.fernet import Fernet
import os

config_groups_bp = Blueprint('config_groups', __name__)


def get_encryption_key():
    """获取加密密钥"""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY not found in environment")
    return Fernet(key.encode())


@config_groups_bp.route('/admin/config-groups', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_all_config_groups():
    """获取所有配置组 - 管理员功能"""
    try:
        current_user_id = int(get_jwt_identity())

        # 获取所有配置组及其配置项
        db = get_db()

        groups = db.execute('''
            SELECT id, name, description, is_active, created_at, updated_at
            FROM config_groups
            ORDER BY created_at DESC
        ''').fetchall()

        groups_list = []
        for group in groups:
            # 获取该组的所有配置项
            settings = db.execute('''
                SELECT key, value, is_encrypted
                FROM system_settings
                WHERE group_id = ?
            ''', (group['id'],)).fetchall()

            settings_dict = {}
            for setting in settings:
                value = setting['value']
                # 如果是加密的，只显示部分内容
                if setting['is_encrypted'] and value:
                    value = value[:10] + '****' + value[-4:]
                settings_dict[setting['key']] = value

            groups_list.append({
                'id': group['id'],
                'name': group['name'],
                'description': group['description'],
                'is_active': bool(group['is_active']),
                'settings': settings_dict,
                'created_at': group['created_at'],
                'updated_at': group['updated_at']
            })

        return jsonify({
            'success': True,
            'groups': groups_list,
            'count': len(groups_list)
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取配置组失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_groups_bp.route('/admin/config-groups', methods=['POST'])
@jwt_required()
@require_role('admin')
def create_config_group():
    """创建新的配置组 - 管理员功能"""
    try:
        current_user_id = int(get_jwt_identity())

        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据无效'
            }), 400

        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        base_url = data.get('base_url', '').strip()
        api_key = data.get('api_key', '').strip()

        # 验证参数
        if not name:
            return jsonify({
                'success': False,
                'error': '配置组名称不能为空'
            }), 400

        if not base_url:
            return jsonify({
                'success': False,
                'error': 'API Base URL 不能为空'
            }), 400

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API Key 不能为空'
            }), 400

        db = get_db()

        # 检查名称是否已存在
        existing = db.execute(
            'SELECT id FROM config_groups WHERE name = ?',
            (name,)
        ).fetchone()

        if existing:
            return jsonify({
                'success': False,
                'error': f'配置组名称 {name} 已存在'
            }), 409

        # 加密API Key
        fernet = get_encryption_key()
        encrypted_api_key = fernet.encrypt(api_key.encode()).decode()

        # 创建配置组
        cursor = db.execute(
            '''INSERT INTO config_groups (name, description, is_active, updated_by)
               VALUES (?, ?, 0, ?)''',
            (name, description, current_user_id)
        )
        group_id = cursor.lastrowid

        # 添加配置项
        db.execute(
            '''INSERT INTO system_settings (group_id, key, value, is_encrypted)
               VALUES (?, ?, ?, ?)''',
            (group_id, 'openai_hk_base_url', base_url, 0)
        )

        db.execute(
            '''INSERT INTO system_settings (group_id, key, value, is_encrypted)
               VALUES (?, ?, ?, ?)''',
            (group_id, 'openai_hk_api_key', encrypted_api_key, 1)
        )

        db.commit()

        current_app.logger.info(f"管理员 {current_user_id} 创建了配置组 {name}")

        return jsonify({
            'success': True,
            'message': f'成功创建配置组 {name}',
            'group_id': group_id
        }), 201

    except Exception as e:
        current_app.logger.error(f"创建配置组失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '创建配置组失败，请稍后重试'
        }), 500


@config_groups_bp.route('/admin/config-groups/<int:group_id>/toggle', methods=['PUT'])
@jwt_required()
@require_role('admin')
def toggle_config_group(group_id):
    """切换配置组启用/禁用状态 - 管理员功能"""
    try:
        current_user_id = int(get_jwt_identity())

        db = get_db()

        # 检查配置组是否存在
        group = db.execute(
            'SELECT id, name, is_active FROM config_groups WHERE id = ?',
            (group_id,)
        ).fetchone()

        if not group:
            return jsonify({
                'success': False,
                'error': '配置组不存在'
            }), 404

        # 切换状态
        new_status = 0 if group['is_active'] else 1

        # 如果要启用，先禁用所有其他配置组
        if new_status == 1:
            db.execute('UPDATE config_groups SET is_active = 0')

        # 更新目标配置组状态
        db.execute(
            'UPDATE config_groups SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (new_status, group_id)
        )
        db.commit()

        action = '启用' if new_status else '禁用'
        current_app.logger.info(f"管理员 {current_user_id} {action}了配置组 {group['name']}")

        return jsonify({
            'success': True,
            'message': f"成功{action}配置组 {group['name']}",
            'is_active': bool(new_status)
        }), 200

    except Exception as e:
        current_app.logger.error(f"切换配置组状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '操作失败，请稍后重试'
        }), 500


@config_groups_bp.route('/admin/config-groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_config_group(group_id):
    """删除配置组 - 管理员功能"""
    try:
        current_user_id = int(get_jwt_identity())

        db = get_db()

        # 检查配置组是否存在
        group = db.execute(
            'SELECT id, name, is_active FROM config_groups WHERE id = ?',
            (group_id,)
        ).fetchone()

        if not group:
            return jsonify({
                'success': False,
                'error': '配置组不存在'
            }), 404

        # 检查是否为启用状态
        if group['is_active']:
            return jsonify({
                'success': False,
                'error': f"配置组 {group['name']} 当前已启用，请先禁用后再删除"
            }), 403

        # 删除配置组（级联删除配置项）
        db.execute('DELETE FROM config_groups WHERE id = ?', (group_id,))
        db.commit()

        current_app.logger.info(f"管理员 {current_user_id} 删除了配置组 {group['name']}")

        return jsonify({
            'success': True,
            'message': f"成功删除配置组 {group['name']}"
        }), 200

    except Exception as e:
        current_app.logger.error(f"删除配置组失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除失败，请稍后重试'
        }), 500


@config_groups_bp.route('/admin/config-groups/<int:group_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_config_group(group_id):
    """更新配置组 - 管理员功能"""
    try:
        current_user_id = int(get_jwt_identity())

        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据无效'
            }), 400

        db = get_db()

        # 检查配置组是否存在
        group = db.execute(
            'SELECT id, name FROM config_groups WHERE id = ?',
            (group_id,)
        ).fetchone()

        if not group:
            return jsonify({
                'success': False,
                'error': '配置组不存在'
            }), 404

        # 更新 base_url
        base_url = data.get('base_url')
        if base_url:
            db.execute(
                '''UPDATE system_settings
                   SET value = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE group_id = ? AND key = ?''',
                (base_url.strip(), group_id, 'openai_hk_base_url')
            )

        # 更新 api_key
        api_key = data.get('api_key')
        if api_key:
            fernet = get_encryption_key()
            encrypted_api_key = fernet.encrypt(api_key.encode()).decode()
            db.execute(
                '''UPDATE system_settings
                   SET value = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE group_id = ? AND key = ?''',
                (encrypted_api_key, group_id, 'openai_hk_api_key')
            )

        # 更新配置组信息
        description = data.get('description')
        if description is not None:
            db.execute(
                '''UPDATE config_groups
                   SET description = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (description.strip(), group_id)
            )

        db.commit()

        current_app.logger.info(f"管理员 {current_user_id} 更新了配置组 {group['name']}")

        return jsonify({
            'success': True,
            'message': f"成功更新配置组 {group['name']}"
        }), 200

    except Exception as e:
        current_app.logger.error(f"更新配置组失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新失败，请稍后重试'
        }), 500