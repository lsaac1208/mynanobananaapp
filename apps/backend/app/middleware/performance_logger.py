"""
性能日志中间件
记录请求性能和慢查询
"""
import time
import logging
from flask import request, g, current_app
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


class PerformanceLogger:
    """性能日志记录器"""
    
    SLOW_REQUEST_THRESHOLD = 1.0  # 慢请求阈值（秒）
    VERY_SLOW_REQUEST_THRESHOLD = 3.0  # 非常慢的请求阈值（秒）
    
    @staticmethod
    def init_app(app):
        """初始化性能日志中间件"""
        
        @app.before_request
        def before_request():
            """请求开始前记录时间"""
            g.start_time = time.time()
            g.request_id = request.headers.get('X-Request-ID', 'unknown')
        
        @app.after_request
        def after_request(response):
            """请求结束后记录性能"""
            if not hasattr(g, 'start_time'):
                return response
            
            duration = time.time() - g.start_time
            
            # 添加响应头
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
            
            # 记录请求信息
            log_data = {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': f"{duration:.3f}s",
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'unknown')[:100]
            }
            
            # 根据响应时间选择日志级别
            if duration > PerformanceLogger.VERY_SLOW_REQUEST_THRESHOLD:
                logger.error(
                    f"🔴 VERY SLOW REQUEST: {log_data['method']} {log_data['path']} "
                    f"took {log_data['duration']} (Status: {log_data['status']})"
                )
            elif duration > PerformanceLogger.SLOW_REQUEST_THRESHOLD:
                logger.warning(
                    f"🟡 SLOW REQUEST: {log_data['method']} {log_data['path']} "
                    f"took {log_data['duration']} (Status: {log_data['status']})"
                )
            else:
                logger.debug(
                    f"✅ {log_data['method']} {log_data['path']} "
                    f"took {log_data['duration']} (Status: {log_data['status']})"
                )
            
            # 记录错误响应
            if response.status_code >= 500:
                logger.error(
                    f"❌ SERVER ERROR: {log_data['method']} {log_data['path']} "
                    f"returned {log_data['status']}"
                )
            elif response.status_code >= 400:
                logger.warning(
                    f"⚠️ CLIENT ERROR: {log_data['method']} {log_data['path']} "
                    f"returned {log_data['status']}"
                )
            
            return response
        
        @app.teardown_request
        def teardown_request(exception=None):
            """请求结束时清理"""
            if exception:
                logger.error(f"❌ Request exception: {str(exception)}")


def log_performance(operation_name: str):
    """
    性能日志装饰器
    用于记录特定操作的执行时间
    
    Usage:
        @log_performance('database_query')
        def get_user(user_id):
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            operation_id = f"{operation_name}:{f.__name__}"
            
            logger.debug(f"⏱️ Starting {operation_id}")
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                if duration > 0.5:
                    logger.warning(
                        f"🟡 {operation_id} took {duration:.3f}s"
                    )
                else:
                    logger.debug(
                        f"✅ {operation_id} completed in {duration:.3f}s"
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"❌ {operation_id} failed after {duration:.3f}s: {str(e)}"
                )
                raise
        
        return decorated_function
    return decorator


class DatabaseQueryLogger:
    """数据库查询日志记录器"""
    
    SLOW_QUERY_THRESHOLD = 0.1  # 慢查询阈值（秒）
    
    @staticmethod
    def log_query(query: str, params: tuple = None, duration: float = 0):
        """
        记录数据库查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            duration: 查询耗时
        """
        # 清理查询语句（移除多余空白）
        clean_query = ' '.join(query.split())
        
        if duration > DatabaseQueryLogger.SLOW_QUERY_THRESHOLD:
            logger.warning(
                f"🐌 SLOW QUERY ({duration:.3f}s): {clean_query[:200]}"
            )
            if params:
                logger.debug(f"   Parameters: {params}")
        else:
            logger.debug(
                f"🔍 Query ({duration:.3f}s): {clean_query[:100]}"
            )


class MemoryMonitor:
    """内存使用监控"""
    
    @staticmethod
    def log_memory_usage():
        """记录当前内存使用情况"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb > 500:  # 超过500MB警告
                logger.warning(
                    f"⚠️ High memory usage: {memory_mb:.2f} MB"
                )
            else:
                logger.debug(
                    f"💾 Memory usage: {memory_mb:.2f} MB"
                )
                
            return memory_mb
            
        except ImportError:
            logger.debug("psutil not available for memory monitoring")
            return None
        except Exception as e:
            logger.error(f"Failed to get memory usage: {str(e)}")
            return None


def monitor_endpoint_performance(endpoint_name: str):
    """
    端点性能监控装饰器
    记录端点的详细性能信息
    
    Usage:
        @monitor_endpoint_performance('user_login')
        def login():
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            
            # 记录请求信息
            logger.info(
                f"📍 Endpoint: {endpoint_name} | "
                f"Method: {request.method} | "
                f"IP: {request.remote_addr}"
            )
            
            # 记录请求参数（不包括敏感信息）
            if request.method == 'GET':
                logger.debug(f"   Query params: {dict(request.args)}")
            elif request.method == 'POST':
                # 不记录密码等敏感字段
                safe_data = {
                    k: v for k, v in request.get_json(silent=True, force=True).items()
                    if k not in ['password', 'api_key', 'secret']
                } if request.is_json else {}
                logger.debug(f"   Request data: {safe_data}")
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"✅ {endpoint_name} completed in {duration:.3f}s"
                )
                
                # 记录内存使用（仅在慢请求时）
                if duration > 1.0:
                    MemoryMonitor.log_memory_usage()
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"❌ {endpoint_name} failed after {duration:.3f}s: {str(e)}"
                )
                raise
        
        return decorated_function
    return decorator


# 导出公共接口
__all__ = [
    'PerformanceLogger',
    'log_performance',
    'DatabaseQueryLogger',
    'MemoryMonitor',
    'monitor_endpoint_performance'
]

