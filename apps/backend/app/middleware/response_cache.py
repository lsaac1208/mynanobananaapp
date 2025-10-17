"""
API响应缓存中间件
用于缓存只读API端点的响应，减少数据库查询和计算开销
"""

from functools import wraps
from flask import request, jsonify, current_app
import hashlib
import json
import time
from typing import Dict, Any, Tuple, Callable, Optional
from datetime import datetime, timedelta

class ResponseCache:
    """响应缓存管理类"""
    
    def __init__(self):
        # cache: { cache_key: (response_data, expire_time) }
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存的响应
        :param key: 缓存键
        :return: 缓存的响应数据，如果不存在或过期则返回None
        """
        if key in self.cache:
            data, expire_time = self.cache[key]
            if time.time() < expire_time:
                self.hit_count += 1
                current_app.logger.debug(f"✅ Cache HIT: {key}")
                return data
            else:
                # 缓存已过期，删除
                del self.cache[key]
                current_app.logger.debug(f"⏰ Cache EXPIRED: {key}")
        
        self.miss_count += 1
        current_app.logger.debug(f"❌ Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        """
        设置缓存
        :param key: 缓存键
        :param value: 要缓存的响应数据
        :param ttl_seconds: 过期时间（秒）
        """
        expire_time = time.time() + ttl_seconds
        self.cache[key] = (value, expire_time)
        current_app.logger.debug(f"💾 Cache SET: {key}, TTL: {ttl_seconds}s")
    
    def invalidate(self, pattern: Optional[str] = None):
        """
        清除缓存
        :param pattern: 如果提供，只清除匹配该模式的键；否则清除所有缓存
        """
        if pattern:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
            current_app.logger.info(f"🗑️  Invalidated {len(keys_to_delete)} cache entries matching '{pattern}'")
        else:
            count = len(self.cache)
            self.cache.clear()
            current_app.logger.info(f"🗑️  Cleared all {count} cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_cached_items': len(self.cache),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': f"{hit_rate:.2f}%"
        }
    
    def cleanup_expired(self):
        """清理所有过期的缓存条目"""
        now = time.time()
        expired_keys = [k for k, (_, expire_time) in self.cache.items() if now >= expire_time]
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            current_app.logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")

# 全局缓存实例
response_cache = ResponseCache()

def cache_response(ttl: int = 60, use_user_id: bool = True, use_query_string: bool = True):
    """
    响应缓存装饰器
    
    :param ttl: 缓存过期时间（秒），默认60秒
    :param use_user_id: 是否将用户ID作为缓存key的一部分，默认True
    :param use_query_string: 是否将查询字符串作为缓存key的一部分，默认True
    
    使用示例:
    @cache_response(ttl=600, use_user_id=False)  # 所有用户共享缓存，10分钟过期
    def get_public_data():
        ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # 生成缓存key
            cache_key_parts = [f.__name__]
            
            # 如果需要，添加用户ID
            if use_user_id:
                from flask_jwt_extended import get_jwt_identity
                try:
                    user_id = get_jwt_identity()
                    cache_key_parts.append(f"user_{user_id}")
                except RuntimeError:
                    # 未认证的请求，使用IP地址
                    cache_key_parts.append(f"ip_{request.remote_addr}")
            
            # 如果需要，添加查询字符串
            if use_query_string and request.query_string:
                cache_key_parts.append(request.query_string.decode('utf-8'))
            
            # 添加请求方法
            cache_key_parts.append(request.method)
            
            # 生成MD5哈希作为缓存key
            cache_key_str = ':'.join(cache_key_parts)
            cache_key = hashlib.md5(cache_key_str.encode()).hexdigest()
            
            # 检查缓存
            cached_response = response_cache.get(cache_key)
            if cached_response is not None:
                # 返回缓存的响应
                return cached_response
            
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 只缓存成功的响应（状态码200）
            if isinstance(result, tuple):
                response_data, status_code = result[0], result[1] if len(result) > 1 else 200
            else:
                response_data = result
                status_code = 200
            
            if status_code == 200:
                response_cache.set(cache_key, result, ttl)
            
            return result
        
        return decorated_function
    return decorator

def invalidate_cache_by_pattern(pattern: str):
    """
    辅助函数：按模式清除缓存
    可以在视图函数中调用，当数据更新时清除相关缓存
    
    使用示例:
    @app.route('/api/settings', methods=['PUT'])
    def update_settings():
        # 更新设置...
        invalidate_cache_by_pattern('get_settings')
        return jsonify({'success': True})
    """
    response_cache.invalidate(pattern)

def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    return response_cache.get_stats()

