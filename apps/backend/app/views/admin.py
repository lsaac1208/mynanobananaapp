"""
管理员相关视图
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import User, SystemSettings
from app.utils.permissions import require_role
from app.repositories.api_config_repository import APIConfigRepository
from app.services.encryption_service import encryption_service
import aiohttp
import asyncio
import re

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/add-credits', methods=['POST'])
@jwt_required()
@require_role('admin')
def add_credits():
    """管理员为用户添加次数"""
    try:
        current_user_id = get_jwt_identity()

        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据无效'
            }), 400

        user_email = data.get('user_email')
        credits = data.get('credits')

        # 验证参数
        if not user_email:
            return jsonify({
                'success': False,
                'error': '用户邮箱不能为空'
            }), 400

        if not credits or not isinstance(credits, int) or credits <= 0:
            return jsonify({
                'success': False,
                'error': '充值次数必须是正整数'
            }), 400

        if credits > 1000:
            return jsonify({
                'success': False,
                'error': '单次充值次数不能超过1000'
            }), 400

        # 查找目标用户
        target_user = User.get_by_email(user_email)
        if not target_user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404

        # 记录充值前的次数
        old_credits = target_user['credits']

        # 执行充值
        User.add_credits(target_user['id'], credits)

        # 获取充值后的用户信息
        updated_user = User.get_by_id(target_user['id'])

        current_app.logger.info(
            f"管理员 {current_user_id} 为用户 {user_email} "
            f"充值 {credits} 次数，从 {old_credits} 增加到 {updated_user['credits']}"
        )

        return jsonify({
            'success': True,
            'message': f'成功为用户 {user_email} 充值 {credits} 次数',
            'data': {
                'user_email': user_email,
                'user_id': target_user['id'],
                'credits_added': credits,
                'old_credits': old_credits,
                'new_credits': updated_user['credits']
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"管理员充值失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '充值失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/users/search', methods=['GET'])
@jwt_required()
@require_role('admin')
def search_users():
    """搜索用户 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 获取搜索参数
        query = request.args.get('q', '').strip()

        # 搜索用户（简化版本，在生产环境中应该使用更高效的搜索）
        from app.database import get_db
        db = get_db()

        if not query:
            # 空搜索返回所有用户
            users = db.execute(
                '''SELECT id, email, credits, is_active, created_at, last_login_at
                   FROM users
                   ORDER BY created_at DESC
                   LIMIT 50''',
            ).fetchall()
        else:
            # 有搜索关键词时进行模糊匹配
            if len(query) < 2:
                return jsonify({
                    'success': False,
                    'error': '搜索关键词至少2个字符'
                }), 400

            users = db.execute(
                '''SELECT id, email, credits, is_active, created_at, last_login_at
                   FROM users
                   WHERE email LIKE ?
                   ORDER BY created_at DESC
                   LIMIT 20''',
                (f'%{query}%',)
            ).fetchall()

        users_list = [dict(user) for user in users]

        return jsonify({
            'success': True,
            'users': users_list,
            'count': len(users_list)
        }), 200

    except Exception as e:
        current_app.logger.error(f"搜索用户失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '搜索失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_user_details(user_id):
    """获取用户详细信息 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 获取用户信息
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404

        # 获取用户的创作统计
        from app.database import Creation
        stats = Creation.get_user_stats(user_id)

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'credits': user['credits'],
                'is_active': user['is_active'],
                'created_at': user['created_at'],
                'last_login_at': user['last_login_at']
            },
            'stats': stats
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取用户详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取用户信息失败'
        }), 500


@admin_bp.route('/admin/settings', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_settings():
    """获取所有系统配置 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 获取所有配置（加密字段自动脱敏）
        settings = SystemSettings.get_all(mask_encrypted=True)

        return jsonify({
            'success': True,
            'settings': settings
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取系统配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取配置失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/settings', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_settings():
    """更新系统配置 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 获取请求数据
        data = request.get_json()
        if not data or 'settings' not in data:
            return jsonify({
                'success': False,
                'error': '请求数据无效'
            }), 400

        settings_to_update = data['settings']
        if not isinstance(settings_to_update, list):
            return jsonify({
                'success': False,
                'error': '配置数据格式错误'
            }), 400

        # 更新每个配置
        updated_count = 0
        failed_items = []

        for setting_item in settings_to_update:
            key = setting_item.get('key')
            value = setting_item.get('value')

            if not key:
                failed_items.append({'key': key, 'reason': '配置键名不能为空'})
                continue

            # 获取配置的加密标志
            from app.database import get_db
            db = get_db()
            existing = db.execute(
                'SELECT is_encrypted, description FROM system_settings WHERE key = ?',
                (key,)
            ).fetchone()

            if not existing:
                failed_items.append({'key': key, 'reason': '配置不存在'})
                continue

            is_encrypted = bool(existing['is_encrypted'])
            description = existing['description']

            # 更新配置
            success = SystemSettings.set(
                key=key,
                value=value,
                description=description,
                is_encrypted=is_encrypted,
                updated_by=current_user_id
            )

            if success:
                updated_count += 1
            else:
                failed_items.append({'key': key, 'reason': '更新失败'})

        # 如果有配置更新成功，清除 AI 生成服务的配置缓存
        if updated_count > 0:
            try:
                from app.services.config_cache import ConfigCache
                ConfigCache.invalidate()
                current_app.logger.info("✅ AI配置缓存已清除")
            except Exception as cache_error:
                current_app.logger.warning(f"清除缓存失败: {str(cache_error)}")
        
        current_app.logger.info(
            f"管理员 {current_user_id} 更新了 {updated_count} 个系统配置"
        )

        return jsonify({
            'success': True,
            'message': f'成功更新 {updated_count} 个配置',
            'updated_count': updated_count,
            'failed_items': failed_items
        }), 200

    except Exception as e:
        current_app.logger.error(f"更新系统配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新配置失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/settings/test-connection', methods=['POST'])
@jwt_required()
@require_role('admin')
def test_api_connection():
    """测试API连接 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 获取请求数据（可选，可以测试新配置而不保存）
        data = request.get_json() or {}
        test_base_url = data.get('base_url')
        test_api_key = data.get('api_key')

        # 如果没有提供测试参数，使用当前数据库配置
        if not test_base_url:
            test_base_url = SystemSettings.get('openai_hk_base_url') or 'https://api.openai-hk.com'

        if not test_api_key:
            test_api_key = SystemSettings.get('openai_hk_api_key')

        if not test_api_key:
            return jsonify({
                'success': False,
                'error': 'API密钥未配置'
            }), 400

        # 测试API连接（调用模型列表接口）
        async def test_connection():
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {test_api_key}',
                    'Content-Type': 'application/json'
                }

                test_url = f"{test_base_url.rstrip('/')}/v1/models"

                try:
                    async with session.get(
                        test_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        status = response.status
                        response_text = await response.text()

                        if status == 200:
                            return {
                                'success': True,
                                'message': 'API连接测试成功',
                                'status_code': status
                            }
                        else:
                            return {
                                'success': False,
                                'message': f'API连接失败: HTTP {status}',
                                'status_code': status,
                                'error_detail': response_text[:200] if response_text else 'No response body'
                            }
                except aiohttp.ClientError as e:
                    return {
                        'success': False,
                        'message': f'网络错误: {str(e)}',
                        'status_code': 0
                    }

        # 运行异步测试
        result = asyncio.run(test_connection())

        current_app.logger.info(
            f"管理员 {current_user_id} 测试API连接: {result['message']}"
        )

        return jsonify(result), 200 if result['success'] else 400

    except asyncio.TimeoutError:
        return jsonify({
            'success': False,
            'error': 'API连接超时，请检查网络或Base URL配置'
        }), 408

    except Exception as e:
        current_app.logger.error(f"测试API连接失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'连接测试失败: {str(e)}'
        }), 500


@admin_bp.route('/admin/settings/all', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_all_settings():
    """获取所有系统配置（包括隐藏的配置项）- 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 获取所有配置（加密字段自动脱敏）
        from app.database import get_db
        db = get_db()

        settings = db.execute(
            '''SELECT key, value, description, is_encrypted,
                      updated_at, updated_by
               FROM system_settings
               ORDER BY key ASC'''
        ).fetchall()

        settings_list = []
        for setting in settings:
            setting_dict = dict(setting)

            # 对加密字段进行脱敏处理
            if setting_dict['is_encrypted'] and setting_dict['value']:
                # 显示前4个字符和后4个字符
                value = setting_dict['value']
                if len(value) > 12:
                    setting_dict['value'] = f"{value[:4]}****{value[-4:]}"
                else:
                    setting_dict['value'] = "****"

            settings_list.append(setting_dict)

        return jsonify({
            'success': True,
            'settings': settings_list,
            'count': len(settings_list)
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取所有配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取配置列表失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/settings/<key>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_single_setting(key):
    """更新单个配置项 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 验证配置键名
        if not key:
            return jsonify({
                'success': False,
                'error': '配置键名不能为空'
            }), 400

        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据无效'
            }), 400

        new_value = data.get('value')
        if new_value is None:
            return jsonify({
                'success': False,
                'error': '配置值不能为空'
            }), 400

        # 检查配置是否存在
        from app.database import get_db
        db = get_db()
        existing = db.execute(
            'SELECT is_encrypted, description FROM system_settings WHERE key = ?',
            (key,)
        ).fetchone()

        if not existing:
            return jsonify({
                'success': False,
                'error': '配置不存在'
            }), 404

        is_encrypted = bool(existing['is_encrypted'])
        description = existing['description']

        # 更新配置
        success = SystemSettings.set(
            key=key,
            value=new_value,
            description=description,
            is_encrypted=is_encrypted,
            updated_by=current_user_id
        )

        if not success:
            return jsonify({
                'success': False,
                'error': '更新配置失败'
            }), 500

        current_app.logger.info(
            f"管理员 {current_user_id} 更新了配置 {key}"
        )

        return jsonify({
            'success': True,
            'message': f'成功更新配置 {key}'
        }), 200

    except Exception as e:
        current_app.logger.error(f"更新单个配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新配置失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/settings', methods=['POST'])
@jwt_required()
@require_role('admin')
def create_setting():
    """创建新的配置项 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据无效'
            }), 400

        key = data.get('key')
        value = data.get('value')
        description = data.get('description', '')
        is_encrypted = data.get('is_encrypted', False)

        # 验证必填字段
        if not key or not value:
            return jsonify({
                'success': False,
                'error': '配置键名和值不能为空'
            }), 400

        # 检查配置键名是否已存在
        from app.database import get_db
        db = get_db()
        existing = db.execute(
            'SELECT key FROM system_settings WHERE key = ?',
            (key,)
        ).fetchone()

        if existing:
            return jsonify({
                'success': False,
                'error': f'配置 {key} 已存在，请使用更新接口'
            }), 400

        # 创建新配置（默认为禁用状态）
        success = SystemSettings.set(
            key=key,
            value=value,
            description=description,
            is_encrypted=is_encrypted,
            updated_by=current_user_id
        )

        if not success:
            return jsonify({
                'success': False,
                'error': '创建配置失败'
            }), 500

        current_app.logger.info(
            f"管理员 {current_user_id} 创建了新配置 {key}"
        )

        return jsonify({
            'success': True,
            'message': f'成功创建配置 {key}'
        }), 201

    except Exception as e:
        current_app.logger.error(f"创建配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '创建配置失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/settings/<key>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_setting(key):
    """删除单个配置项 - 管理员功能"""
    try:
        current_user_id = get_jwt_identity()

        # 验证配置键名
        if not key:
            return jsonify({
                'success': False,
                'error': '配置键名不能为空'
            }), 400

        # 检查配置是否存在
        from app.database import get_db
        db = get_db()
        existing = db.execute(
            'SELECT key FROM system_settings WHERE key = ?',
            (key,)
        ).fetchone()

        if not existing:
            return jsonify({
                'success': False,
                'error': '配置不存在'
            }), 404

        # 删除配置
        db.execute('DELETE FROM system_settings WHERE key = ?', (key,))
        db.commit()

        current_app.logger.info(
            f"管理员 {current_user_id} 删除了配置 {key}"
        )

        return jsonify({
            'success': True,
            'message': f'成功删除配置 {key}'
        }), 200

    except Exception as e:
        current_app.logger.error(f"删除配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除配置失败，请稍后重试'
        }), 500


@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_user(user_id):
    """删除用户 - 管理员功能

    级联删除策略：
    - 软删除：作品标记为孤儿（保留内容）
    - 硬删除：会话、行为、偏好、推荐、性能指标
    - 审计日志：记录删除操作和影响范围
    """
    try:
        current_user_id = get_jwt_identity()

        # 防止管理员删除自己
        if current_user_id == user_id:
            return jsonify({
                'success': False,
                'error': '不能删除自己的账户'
            }), 400

        # 获取可选的删除原因
        reason = request.args.get('reason', '')

        # 执行级联删除
        result = User.delete_user_cascade(
            user_id=user_id,
            admin_id=current_user_id,
            reason=reason
        )

        current_app.logger.info(
            f"管理员 {current_user_id} 删除了用户 {result['deleted_user']['email']} (ID: {user_id})"
        )

        return jsonify({
            'success': True,
            'message': result['message'],
            'deleted_user': result['deleted_user'],
            'impact': result['impact']
        }), 200

    except ValueError as e:
        # 用户不存在
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

    except Exception as e:
        current_app.logger.error(f"删除用户失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除用户失败，请稍后重试',
            'details': str(e)
        }), 500

# ========================================
# API配置管理路由 (API Configuration Management)
# ========================================

# Repository instance for API configuration operations
config_repo = APIConfigRepository()


def _validate_url(url: str) -> bool:
    """Validate URL format."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return url_pattern.match(url) is not None


@admin_bp.route('/admin/config-groups', methods=['GET'])
@jwt_required()
@require_role('admin')
def list_config_groups():
    """
    列出所有API配置组
    Returns all API configuration groups with masked API keys
    """
    try:
        configs = config_repo.get_all()

        # Mask API keys in response (show last 4 chars only)
        for config in configs:
            if config.get('settings') and config['settings'].get('openai_hk_api_key'):
                key = config['settings']['openai_hk_api_key']
                config['settings']['openai_hk_api_key'] = f"****{key[-4:]}" if len(key) > 4 else "****"

        return jsonify({
            'status': 'success',
            'data': configs,
            'count': len(configs)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to list config groups: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '获取配置列表失败'
        }), 500


@admin_bp.route('/admin/config-groups', methods=['POST'])
@jwt_required()
@require_role('admin')
def create_config_group():
    """
    创建新的API配置组
    Create new API configuration group

    Request Body:
    {
        "name": "Production API",
        "description": "Main production API configuration",
        "openai_hk_base_url": "https://api.openai-hk.com",
        "openai_hk_api_key": "sk-xxxxx",
        "is_active": false
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Input validation
        required_fields = ['name', 'openai_hk_base_url', 'openai_hk_api_key']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必填字段: {field}'
                }), 400

        # Validate field lengths
        if len(data['name']) > 100:
            return jsonify({
                'status': 'error',
                'message': '配置名称过长 (最多100字符)'
            }), 400

        # Validate URL format
        if not _validate_url(data['openai_hk_base_url']):
            return jsonify({
                'status': 'error',
                'message': 'Base URL格式无效'
            }), 400

        # Validate API key length
        if len(data['openai_hk_api_key']) < 10:
            return jsonify({
                'status': 'error',
                'message': 'API Key长度不能少于10个字符'
            }), 400

        # Check name uniqueness
        if config_repo.get_by_name(data['name']):
            return jsonify({
                'status': 'error',
                'message': f"配置名称 '{data['name']}' 已存在"
            }), 409

        # Encrypt API key
        encrypted_key = encryption_service.encrypt(data['openai_hk_api_key'])

        # Create configuration
        config_id = config_repo.create(
            name=data['name'],
            description=data.get('description', ''),
            openai_hk_base_url=data['openai_hk_base_url'],
            openai_hk_api_key_encrypted=encrypted_key,
            is_active=data.get('is_active', False)
        )

        current_app.logger.info(
            f"管理员 {current_user_id} 创建了API配置: {data['name']} (ID: {config_id})"
        )

        return jsonify({
            'status': 'success',
            'message': '配置创建成功',
            'data': {'id': config_id}
        }), 201

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

    except Exception as e:
        current_app.logger.error(f"Failed to create config group: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '创建配置失败'
        }), 500


@admin_bp.route('/admin/config-groups/<int:config_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_config_group(config_id):
    """
    更新API配置组
    Update existing API configuration group
    """
    try:
        current_user_id = get_jwt_identity()

        # Verify config exists
        existing = config_repo.get_by_id(config_id)
        if not existing:
            return jsonify({
                'status': 'error',
                'message': f'配置ID {config_id} 不存在'
            }), 404

        data = request.get_json()

        # Prepare update data
        update_data = {}

        if 'name' in data:
            # Check name uniqueness (excluding current config)
            name_conflict = config_repo.get_by_name(data['name'])
            if name_conflict and name_conflict['id'] != config_id:
                return jsonify({
                    'status': 'error',
                    'message': f"配置名称 '{data['name']}' 已存在"
                }), 409
            update_data['name'] = data['name']

        if 'description' in data:
            update_data['description'] = data['description']

        if 'openai_hk_base_url' in data:
            if not _validate_url(data['openai_hk_base_url']):
                return jsonify({
                    'status': 'error',
                    'message': 'Base URL格式无效'
                }), 400
            update_data['openai_hk_base_url'] = data['openai_hk_base_url']

        if 'openai_hk_api_key' in data:
            # Re-encrypt new API key
            update_data['openai_hk_api_key_encrypted'] = encryption_service.encrypt(
                data['openai_hk_api_key']
            )

        if 'is_active' in data:
            update_data['is_active'] = bool(data['is_active'])

        # Perform update
        config_repo.update(config_id, **update_data)

        current_app.logger.info(
            f"管理员 {current_user_id} 更新了API配置ID {config_id}"
        )

        return jsonify({
            'status': 'success',
            'message': '配置更新成功'
        }), 200

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

    except Exception as e:
        current_app.logger.error(f"Failed to update config group {config_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '更新配置失败'
        }), 500


@admin_bp.route('/admin/config-groups/<int:config_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_config_group(config_id):
    """
    删除API配置组
    Delete API configuration group
    """
    try:
        current_user_id = get_jwt_identity()

        # Verify config exists
        existing = config_repo.get_by_id(config_id)
        if not existing:
            return jsonify({
                'status': 'error',
                'message': f'配置ID {config_id} 不存在'
            }), 404

        # Check if deleting active config
        if existing['is_active']:
            all_configs = config_repo.get_all()
            if len(all_configs) <= 1:
                return jsonify({
                    'status': 'error',
                    'message': '不能删除唯一的激活配置'
                }), 409

        # Perform deletion
        config_repo.delete(config_id)

        current_app.logger.info(
            f"管理员 {current_user_id} 删除了API配置ID {config_id}"
        )

        return jsonify({
            'status': 'success',
            'message': '配置删除成功'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to delete config group {config_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '删除配置失败'
        }), 500


@admin_bp.route('/admin/config-groups/<int:config_id>/toggle', methods=['POST'])
@jwt_required()
@require_role('admin')
def toggle_config_group(config_id):
    """
    切换API配置组激活状态
    Toggle configuration group activation status
    """
    try:
        current_user_id = get_jwt_identity()

        # Verify config exists
        existing = config_repo.get_by_id(config_id)
        if not existing:
            return jsonify({
                'status': 'error',
                'message': f'配置ID {config_id} 不存在'
            }), 404

        new_state = not existing['is_active']

        # Update activation state (trigger handles single active rule)
        config_repo.update(config_id, is_active=new_state)

        action = '激活' if new_state else '停用'
        current_app.logger.info(
            f"管理员 {current_user_id} {action}了API配置ID {config_id}"
        )

        return jsonify({
            'status': 'success',
            'message': f'配置已{action}',
            'data': {'is_active': new_state}
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to toggle config group {config_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '切换配置状态失败'
        }), 500


@admin_bp.route('/admin/test-api-connection', methods=['POST'])
@jwt_required()
@require_role('admin')
def test_config_api_connection():
    """
    测试API配置连接
    Test API connectivity with provided or existing configuration

    Request Body (optional):
    {
        "config_id": 1,  // Test existing config
        OR
        "base_url": "https://api.openai-hk.com",  // Test new credentials
        "api_key": "sk-xxxxx"
    }
    """
    try:
        data = request.get_json() or {}

        # Determine test target
        if 'config_id' in data:
            config = config_repo.get_by_id(data['config_id'])
            if not config:
                return jsonify({
                    'status': 'error',
                    'message': '配置不存在'
                }), 404

            base_url = config['openai_hk_base_url']
            api_key = encryption_service.decrypt(
                config['openai_hk_api_key_encrypted']
            )

        elif 'base_url' in data and 'api_key' in data:
            base_url = data['base_url']
            api_key = data['api_key']

        else:
            # Test active configuration
            active_config = config_repo.get_active()
            if not active_config:
                return jsonify({
                    'status': 'error',
                    'message': '没有激活的配置'
                }), 404

            base_url = active_config['openai_hk_base_url']
            api_key = encryption_service.decrypt(
                active_config['openai_hk_api_key_encrypted']
            )

        # Test API connectivity
        async def test_connection():
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                # Test with models endpoint (lightweight)
                test_url = f"{base_url.rstrip('/')}/v1/models"

                try:
                    async with session.get(test_url, headers=headers) as resp:
                        if resp.status == 200:
                            return True, "连接成功"
                        else:
                            error_text = await resp.text()
                            return False, f"API错误: {resp.status} - {error_text[:100]}"
                except Exception as e:
                    return False, f"连接失败: {str(e)}"

        # Run async test
        success, message = asyncio.run(test_connection())

        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': {'connection_valid': True}
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': message,
                'data': {'connection_valid': False}
            }), 400

    except asyncio.TimeoutError:
        return jsonify({
            'status': 'error',
            'message': '连接超时 - API无法访问',
            'data': {'connection_valid': False}
        }), 408

    except Exception as e:
        current_app.logger.error(f"API connection test failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'连接测试失败: {str(e)}',
            'data': {'connection_valid': False}
        }), 500
