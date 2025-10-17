"""
API请求速率限制中间件
防止API滥用和服务器过载
"""
from functools import wraps
from flask import request, jsonify, current_app
import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    速率限制器
    
    使用滑动窗口算法跟踪请求频率
    支持不同类型的请求限制
    """
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = Lock()
        
        # 不同类型的限制配置 (最大请求数, 时间窗口秒数)
        self.limits = {
            'generate': (10, 60),      # AI生成: 10次/分钟
            'api': (100, 60),           # 一般API: 100次/分钟
            'login': (5, 300),          # 登录: 5次/5分钟
            'register': (3, 3600),      # 注册: 3次/小时
            'gallery': (50, 60),        # 画廊查询: 50次/分钟
        }
    
    def is_allowed(self, key: str, limit_type: str = 'api') -> tuple[bool, int]:
        """
        检查是否允许请求
        
        Args:
            key: 请求标识（用户ID或IP）
            limit_type: 限制类型
            
        Returns:
            (是否允许, 重试等待秒数)
        """
        if limit_type not in self.limits:
            current_app.logger.warning(f"Unknown limit type: {limit_type}, using default 'api'")
            limit_type = 'api'
        
        max_requests, window = self.limits[limit_type]
        now = time.time()
        
        with self.lock:
            # 清理过期的请求记录
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < window
            ]
            
            # 检查是否超过限制
            if len(self.requests[key]) >= max_requests:
                # 计算需要等待的时间
                oldest_request = self.requests[key][0]
                retry_after = int(window - (now - oldest_request)) + 1
                
                current_app.logger.warning(
                    f"Rate limit exceeded for {key} ({limit_type}): "
                    f"{len(self.requests[key])}/{max_requests} in {window}s"
                )
                
                return False, retry_after
            
            # 记录本次请求
            self.requests[key].append(now)
            return True, 0
    
    def get_stats(self, key: str) -> dict:
        """获取指定key的速率统计信息"""
        with self.lock:
            return {
                'total_requests': len(self.requests[key]),
                'oldest_request': self.requests[key][0] if self.requests[key] else None,
                'newest_request': self.requests[key][-1] if self.requests[key] else None
            }
    
    def clear(self, key: str = None):
        """清除速率限制记录（用于测试或管理员操作）"""
        with self.lock:
            if key:
                self.requests.pop(key, None)
            else:
                self.requests.clear()


# 全局速率限制器实例
rate_limiter = RateLimiter()


def rate_limit(limit_type: str = 'api'):
    """
    速率限制装饰器
    
    Args:
        limit_type: 限制类型 ('generate', 'api', 'login', 'register', 'gallery')
    
    Usage:
        @rate_limit('generate')
        def my_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 尝试获取用户ID（已认证用户）
            key = None
            try:
                from flask_jwt_extended import get_jwt_identity
                user_id = get_jwt_identity()
                if user_id:
                    key = f"user:{user_id}"
            except Exception:
                pass
            
            # 如果没有用户ID，使用IP地址
            if not key:
                key = f"ip:{request.remote_addr}"
            
            # 添加限制类型前缀
            rate_key = f"{limit_type}:{key}"
            
            # 检查速率限制
            allowed, retry_after = rate_limiter.is_allowed(rate_key, limit_type)
            
            if not allowed:
                response = {
                    'success': False,
                    'error': 'Too many requests. Please slow down.',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': retry_after
                }
                
                return jsonify(response), 429
            
            # 执行原函数
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def get_request_key():
    """
    获取当前请求的唯一标识
    优先使用用户ID，否则使用IP地址
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
    except Exception:
        pass
    
    return f"ip:{request.remote_addr}"


def check_rate_limit(limit_type: str = 'api') -> tuple[bool, int]:
    """
    手动检查速率限制（不使用装饰器）
    
    Returns:
        (是否允许, 重试等待秒数)
    """
    key = get_request_key()
    rate_key = f"{limit_type}:{key}"
    return rate_limiter.is_allowed(rate_key, limit_type)

