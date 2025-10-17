"""
图片生成相关视图
"""
import asyncio
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_generator import get_ai_generator_service
from app.database import get_db
from app.middleware.rate_limiter import rate_limit
from app.middleware.response_cache import cache_response

generate_bp = Blueprint('generate', __name__)


@generate_bp.route('/generate/models', methods=['GET'])
@cache_response(ttl=600, use_user_id=False, use_query_string=False)  # 10分钟缓存，所有用户共享
def get_available_models():
    """获取可用的模型和尺寸"""
    try:
        ai_service = get_ai_generator_service()
        models = ai_service.get_available_models()
        sizes = ai_service.get_available_sizes()

        return jsonify({
            'success': True,
            'models': models,
            'sizes': sizes
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取可用模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取可用模型失败'
        }), 500


@generate_bp.route('/generate/text-to-image', methods=['POST'])
@jwt_required()
@rate_limit('generate')
def generate_text_to_image():
    """文生图接口"""
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        from app.database import User
        user = User.get_by_id(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # 检查用户次数
        if user['credits'] <= 0:
            return jsonify({'error': 'Insufficient credits'}), 400

        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400

        prompt = data.get('prompt')
        if not prompt or not prompt.strip():
            return jsonify({'error': 'Prompt is required'}), 400

        # 预扣除次数
        if not User.consume_credits(current_user_id, 1):
            return jsonify({'error': 'Insufficient credits'}), 400

        # 准备生成参数
        generation_params = {
            'prompt': prompt.strip(),
            'model': data.get('model', 'nano-banana'),
            'size': data.get('size', '1x1'),
            'quality': data.get('quality', 'standard'),
            'n': min(int(data.get('n', 1)), 4)  # 最多4张
        }

        # 调用AI服务生成图片
        ai_service = get_ai_generator_service()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                ai_service.generate_text_to_image(generation_params, user_id=current_user_id)
            )
        finally:
            loop.close()

        if not result['success']:
            # 生成失败，退还次数
            User.refund_credits(current_user_id, 1)
            return jsonify({
                'success': False,
                'error': result.get('error', 'Generation failed')
            }), 500

        # 保存生成记录并获取完整的Creation对象
        from app.database import Creation
        created_objects = []
        for image in result['images']:
            creation_id = Creation.create(
                user_id=current_user_id,
                prompt=generation_params['prompt'],
                image_url=image['url'],
                model_used=generation_params['model'],
                size=generation_params['size'],
                generation_time=result.get('generation_time')
            )
            # 获取完整的创建对象
            creation = Creation.get_by_id(creation_id)
            if creation:
                created_objects.append(creation)

        # 获取更新后的用户次数
        updated_user = User.get_by_id(current_user_id)

        return jsonify({
            'success': True,
            'images': result['images'],
            'creations': created_objects,
            'generation_time': result.get('generation_time'),
            'model_used': result.get('model_used'),
            'prompt': result.get('prompt'),
            'remaining_credits': updated_user['credits']
        }), 200

    except Exception as e:
        current_app.logger.error(f"文生图失败: {str(e)}")
        # 发生异常时也要退还次数
        try:
            User.refund_credits(current_user_id, 1)
        except:
            pass
        return jsonify({
            'success': False,
            'error': '生成失败，请稍后重试'
        }), 500


@generate_bp.route('/generate/image-to-image', methods=['POST'])
@jwt_required()
@rate_limit('generate')
def generate_image_to_image():
    """图生图接口（支持多图）"""
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        from app.database import User
        user = User.get_by_id(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # 检查用户次数
        if user['credits'] <= 0:
            return jsonify({'error': 'Insufficient credits'}), 400

        # 获取请求参数
        prompt = request.form.get('prompt')
        if not prompt or not prompt.strip():
            return jsonify({'error': 'Prompt is required'}), 400

        # 获取多个图片文件
        images = request.files.getlist('images[]') or request.files.getlist('images')
        
        # 向后兼容：如果没有多图，尝试获取单图
        if not images and 'image' in request.files:
            images = [request.files['image']]
        
        if not images:
            return jsonify({'error': 'At least one image is required'}), 400
        
        if len(images) > 4:
            return jsonify({'error': 'Maximum 4 images allowed'}), 400

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        for image_file in images:
            if image_file.content_type not in allowed_types:
                return jsonify({'error': 'Invalid image format'}), 400

        # 预扣除次数
        if not User.consume_credits(current_user_id, 1):
            return jsonify({'error': 'Insufficient credits'}), 400

        # 准备生成参数
        generation_params = {
            'prompt': prompt.strip(),
            'images': images,
            'model': request.form.get('model', 'nano-banana')
        }

        # 调用AI服务生成图片
        ai_service = get_ai_generator_service()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                ai_service.generate_image_to_image(generation_params, user_id=current_user_id)
            )
        finally:
            loop.close()

        if not result['success']:
            # 生成失败，退还次数
            User.refund_credits(current_user_id, 1)
            return jsonify({
                'success': False,
                'error': result.get('error', 'Generation failed')
            }), 500

        # 保存生成记录并获取完整的Creation对象
        from app.database import Creation
        created_objects = []
        for image in result['images']:
            creation_id = Creation.create(
                user_id=current_user_id,
                prompt=generation_params['prompt'],
                image_url=image['url'],
                model_used=generation_params['model'],
                size='auto',  # 图生图不需要指定尺寸
                generation_time=result.get('generation_time')
            )
            # 获取完整的创建对象
            creation = Creation.get_by_id(creation_id)
            if creation:
                created_objects.append(creation)

        # 获取更新后的用户次数
        updated_user = User.get_by_id(current_user_id)

        return jsonify({
            'success': True,
            'images': result['images'],
            'creations': created_objects,
            'generation_time': result.get('generation_time'),
            'model_used': result.get('model_used'),
            'prompt': result.get('prompt'),
            'remaining_credits': updated_user['credits']
        }), 200

    except Exception as e:
        current_app.logger.error(f"图生图失败: {str(e)}")
        # 发生异常时也要退还次数
        try:
            User.refund_credits(current_user_id, 1)
        except:
            pass
        return jsonify({
            'success': False,
            'error': '生成失败，请稍后重试'
        }), 500


@generate_bp.route('/gallery', methods=['GET'])
@jwt_required()
def get_user_gallery():
    """获取用户作品画廊（支持筛选和搜索）"""
    try:
        current_user_id = get_jwt_identity()

        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)  # 最多50个
        offset = (page - 1) * per_page

        # 获取筛选参数
        category = request.args.get('category')  # 分类筛选
        tags = request.args.get('tags')  # 标签筛选
        search = request.args.get('search')  # 搜索关键词
        is_favorite = request.args.get('is_favorite')  # 收藏筛选

        # 转换收藏参数
        favorite_filter = None
        if is_favorite is not None:
            favorite_filter = is_favorite.lower() == 'true'

        # 获取用户作品（使用新的筛选方法）
        from app.database import Creation
        creations = Creation.get_by_user_with_filters(
            user_id=current_user_id,
            limit=per_page,
            offset=offset,
            category=category,
            tags=tags,
            search=search,
            is_favorite=favorite_filter
        )

        # 获取用户统计信息
        stats = Creation.get_user_stats(current_user_id)

        return jsonify({
            'success': True,
            'creations': creations,
            'page': page,
            'per_page': per_page,
            'stats': stats
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取用户画廊失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取作品列表失败'
        }), 500


@generate_bp.route('/gallery/<int:creation_id>', methods=['DELETE'])
@jwt_required()
def delete_creation(creation_id):
    """删除用户作品"""
    try:
        current_user_id = get_jwt_identity()

        # 删除作品（仅限作品所有者）
        from app.database import Creation
        success = Creation.delete(creation_id, current_user_id)

        if not success:
            return jsonify({
                'success': False,
                'error': '作品不存在或无权删除'
            }), 404

        return jsonify({
            'success': True,
            'message': '作品已删除'
        }), 200

    except Exception as e:
        current_app.logger.error(f"删除作品失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除作品失败'
        }), 500


@generate_bp.route('/gallery/<int:creation_id>/favorite', methods=['PUT'])
@jwt_required()
def toggle_favorite(creation_id):
    """切换作品收藏状态"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        is_favorite = data.get('is_favorite', False)

        from app.database import Creation
        success = Creation.update_favorite(creation_id, current_user_id, is_favorite)

        if not success:
            return jsonify({
                'success': False,
                'error': '作品不存在或无权修改'
            }), 404

        return jsonify({
            'success': True,
            'message': '收藏状态已更新'
        }), 200

    except Exception as e:
        current_app.logger.error(f"更新收藏状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新收藏状态失败'
        }), 500


@generate_bp.route('/gallery/<int:creation_id>/tags', methods=['PUT'])
@jwt_required()
def update_creation_tags(creation_id):
    """更新作品标签"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        tags = data.get('tags', '')

        from app.database import Creation
        success = Creation.update_tags(creation_id, current_user_id, tags)

        if not success:
            return jsonify({
                'success': False,
                'error': '作品不存在或无权修改'
            }), 404

        return jsonify({
            'success': True,
            'message': '标签已更新'
        }), 200

    except Exception as e:
        current_app.logger.error(f"更新作品标签失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新标签失败'
        }), 500


@generate_bp.route('/gallery/<int:creation_id>/category', methods=['PUT'])
@jwt_required()
def update_creation_category(creation_id):
    """更新作品分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        category = data.get('category', 'general')

        from app.database import Creation
        success = Creation.update_category(creation_id, current_user_id, category)

        if not success:
            return jsonify({
                'success': False,
                'error': '作品不存在或无权修改'
            }), 404

        return jsonify({
            'success': True,
            'message': '分类已更新'
        }), 200

    except Exception as e:
        current_app.logger.error(f"更新作品分类失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新分类失败'
        }), 500


@generate_bp.route('/gallery/categories', methods=['GET'])
@jwt_required()
@cache_response(ttl=300)  # 5分钟缓存
def get_user_categories():
    """获取用户使用过的分类"""
    try:
        current_user_id = get_jwt_identity()

        from app.database import Creation
        categories = Creation.get_available_categories(current_user_id)

        return jsonify({
            'success': True,
            'categories': categories
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取分类失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取分类失败'
        }), 500


@generate_bp.route('/gallery/tags', methods=['GET'])
@jwt_required()
@cache_response(ttl=300)  # 5分钟缓存
def get_user_tags():
    """获取用户常用标签"""
    try:
        current_user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 20))

        from app.database import Creation
        tags = Creation.get_popular_tags(current_user_id, limit)

        return jsonify({
            'success': True,
            'tags': tags
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取标签失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取标签失败'
        }), 500


@generate_bp.route('/gallery/stats', methods=['GET'])
@jwt_required()
@cache_response(ttl=120)  # 2分钟缓存，因为统计信息可能变化较频繁
def get_user_gallery_stats():
    """获取用户画廊统计信息"""
    try:
        current_user_id = get_jwt_identity()

        from app.database import Creation
        stats = Creation.get_user_stats(current_user_id)

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取统计信息失败'
        }), 500


@generate_bp.route('/gallery/proxy-image', methods=['POST'])
@jwt_required()
def proxy_image():
    """
    图片代理接口 - 解决画廊图生图的跨域问题
    用于从外部URL获取图片并返回给前端，避免CORS限制
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'image_url' not in data:
            return jsonify({
                'success': False,
                'error': '缺少图片URL参数'
            }), 400

        image_url = data['image_url']

        # 验证URL格式
        if not image_url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': '无效的图片URL'
            }), 400

        # 使用aiohttp异步获取图片
        import aiohttp
        import asyncio

        async def fetch_image():
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.get(image_url) as response:
                        if response.status != 200:
                            raise Exception(f"HTTP {response.status}: {response.reason}")

                        # 检查内容类型
                        content_type = response.headers.get('content-type', '')
                        if not content_type.startswith('image/'):
                            raise Exception(f"不是有效的图片类型: {content_type}")

                        # 检查文件大小（限制10MB）
                        content_length = response.headers.get('content-length')
                        if content_length and int(content_length) > 10 * 1024 * 1024:
                            raise Exception("图片文件过大（超过10MB）")

                        # 读取图片数据
                        image_data = await response.read()

                        # 检查实际大小
                        if len(image_data) > 10 * 1024 * 1024:
                            raise Exception("图片文件过大（超过10MB）")

                        return {
                            'data': image_data,
                            'content_type': content_type,
                            'size': len(image_data)
                        }

                except aiohttp.ClientError as e:
                    raise Exception(f"网络请求失败: {str(e)}")
                except asyncio.TimeoutError:
                    raise Exception("请求超时，请稍后重试")

        # 运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(fetch_image())
        finally:
            loop.close()

        # 返回图片数据（base64编码）
        import base64
        image_base64 = base64.b64encode(result['data']).decode('utf-8')

        current_app.logger.info(f"成功代理图片: {image_url}, 大小: {result['size']} bytes")

        return jsonify({
            'success': True,
            'image_data': f"data:{result['content_type']};base64,{image_base64}",
            'content_type': result['content_type'],
            'size': result['size']
        }), 200

    except Exception as e:
        current_app.logger.error(f"图片代理失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取图片失败: {str(e)}'
        }), 500


# ===== Phase 2: 性能数据分析API接口 =====

@generate_bp.route('/analytics/performance', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """获取系统性能分析数据"""
    try:
        current_user_id = get_jwt_identity()

        # 获取时间范围参数
        hours = int(request.args.get('hours', 24))  # 默认24小时
        operation_type = request.args.get('operation_type')  # 可选的操作类型筛选

        from app.database import PerformanceMetric

        # 获取平均生成时间
        avg_generation_time = PerformanceMetric.get_avg_generation_time(operation_type, hours)

        # 获取错误率
        error_rate = PerformanceMetric.get_error_rate(hours)

        # 获取峰值负载
        peak_load = PerformanceMetric.get_peak_load(hours)

        return jsonify({
            'success': True,
            'analytics': {
                'avg_generation_time': round(avg_generation_time, 2),
                'error_rate': round(error_rate, 2),
                'peak_server_load': round(peak_load, 3),
                'time_range_hours': hours,
                'operation_type': operation_type or 'all'
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取性能分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取性能分析数据失败'
        }), 500


@generate_bp.route('/analytics/user-behavior', methods=['GET'])
@jwt_required()
def get_user_behavior_analytics():
    """获取用户行为分析数据"""
    try:
        current_user_id = get_jwt_identity()

        from app.database import UserBehavior, UserSession

        # 获取用户偏好
        preferences = UserBehavior.get_user_preferences(current_user_id)

        # 获取当前活跃会话数
        active_sessions = UserSession.get_active_sessions_count()

        return jsonify({
            'success': True,
            'user_analytics': {
                'preferred_model': preferences.get('preferred_model'),
                'most_active_hour': preferences.get('most_active_hour'),
                'avg_session_duration': round(preferences.get('avg_session_duration') or 0, 2),
                'current_active_sessions': active_sessions
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取用户行为分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取用户行为分析失败'
        }), 500


@generate_bp.route('/analytics/popular-actions', methods=['GET'])
@jwt_required()
def get_popular_actions():
    """获取热门操作统计"""
    try:
        days = int(request.args.get('days', 7))  # 默认7天

        from app.database import UserBehavior

        # 获取热门操作
        popular_actions = UserBehavior.get_popular_actions(days)

        return jsonify({
            'success': True,
            'popular_actions': popular_actions,
            'time_range_days': days
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取热门操作统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取热门操作统计失败'
        }), 500


@generate_bp.route('/analytics/daily-stats', methods=['GET'])
@jwt_required()
def get_daily_stats():
    """获取每日统计数据"""
    try:
        from app.database import DailyStat

        # 获取最近7天的统计数据
        weekly_stats = DailyStat.get_weekly_stats()

        # 更新今日统计
        DailyStat.update_today()

        return jsonify({
            'success': True,
            'daily_stats': weekly_stats
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取每日统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取每日统计数据失败'
        }), 500


@generate_bp.route('/analytics/system-insights', methods=['GET'])
@jwt_required()
def get_system_insights():
    """获取系统综合洞察"""
    try:
        from app.database import PerformanceMetric, UserSession, Creation
        current_user_id = get_jwt_identity()

        # 获取综合性能指标
        performance_data = {
            'avg_generation_time_24h': PerformanceMetric.get_avg_generation_time(hours=24),
            'avg_generation_time_7d': PerformanceMetric.get_avg_generation_time(hours=168),
            'error_rate_24h': PerformanceMetric.get_error_rate(hours=24),
            'peak_load_24h': PerformanceMetric.get_peak_load(hours=24),
            'active_sessions': UserSession.get_active_sessions_count()
        }

        # 获取系统用户统计（管理员可见）
        db = get_db()
        total_users = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
        active_users = db.execute('SELECT COUNT(*) as count FROM users WHERE is_active = 1').fetchone()['count']
        recent_week_users = db.execute(
            "SELECT COUNT(*) as count FROM users WHERE created_at >= datetime('now', '-7 days')"
        ).fetchone()['count']

        # 获取系统作品统计
        total_creations = db.execute('SELECT COUNT(*) as count FROM creations').fetchone()['count']
        favorites = db.execute('SELECT COUNT(*) as count FROM creations WHERE is_favorite = 1').fetchone()['count']

        # 按分类统计
        categories_stats = db.execute(
            'SELECT category, COUNT(*) as count FROM creations GROUP BY category'
        ).fetchall()

        user_stats = {
            'total': total_users,  # 系统总用户数
            'active': active_users,  # 活跃用户数
            'recent_week': recent_week_users,  # 本周新增用户
            'total_creations': total_creations,  # 系统总作品数
            'favorites': favorites,  # 收藏作品数
            'categories': [{'category': c['category'], 'count': c['count']} for c in categories_stats]
        }

        # 生成优化建议
        insights = []
        if performance_data['error_rate_24h'] > 5:
            insights.append({
                'type': 'warning',
                'message': f"系统错误率较高 ({performance_data['error_rate_24h']:.1f}%)，建议检查服务状态",
                'priority': 'high'
            })

        if performance_data['avg_generation_time_24h'] > 60:
            insights.append({
                'type': 'info',
                'message': f"平均生成时间较长 ({performance_data['avg_generation_time_24h']:.1f}s)，可能需要优化",
                'priority': 'medium'
            })

        if performance_data['peak_load_24h'] > 0.8:
            insights.append({
                'type': 'warning',
                'message': f"服务器负载较高 ({performance_data['peak_load_24h']:.2f})，建议扩容",
                'priority': 'high'
            })

        if user_stats['recent_week'] == 0:
            insights.append({
                'type': 'suggestion',
                'message': "您最近一周没有创作，试试新的提示词吧！",
                'priority': 'low'
            })

        return jsonify({
            'success': True,
            'system_insights': {
                'performance': performance_data,
                'user_stats': user_stats,
                'insights': insights,
                'overall_health': 'good' if performance_data['error_rate_24h'] < 2 else 'warning'
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取系统洞察失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取系统洞察数据失败'
        }), 500


