"""
配置缓存管理
提供 AI 生成服务配置的缓存机制，减少数据库查询次数
"""
import time
from typing import Optional, Dict, Any
import threading


class ConfigCache:
    """
    配置缓存管理类
    
    使用单例模式实现全局配置缓存，支持：
    - TTL（生存时间）管理
    - 线程安全
    - 手动失效
    """
    
    # 类级别的缓存存储
    _cache: Optional[Dict[str, Any]] = None
    _cache_time: float = 0
    _lock = threading.Lock()
    
    # 缓存配置
    CACHE_TTL = 300  # 5分钟 (300秒)
    
    @classmethod
    def get_config(cls) -> Optional[Dict[str, Any]]:
        """
        获取缓存的配置
        
        Returns:
            Dict[str, Any]: 配置字典，如果缓存无效则返回 None
        """
        with cls._lock:
            if cls._is_valid():
                return cls._cache.copy() if cls._cache else None
            return None
    
    @classmethod
    def set_config(cls, config: Dict[str, Any]) -> None:
        """
        设置配置缓存
        
        Args:
            config: 配置字典，包含 base_url 和 api_key
        """
        with cls._lock:
            cls._cache = config.copy() if config else None
            cls._cache_time = time.time()
    
    @classmethod
    def invalidate(cls) -> None:
        """
        使缓存失效
        
        用于管理员更新配置后立即清除缓存
        """
        with cls._lock:
            cls._cache = None
            cls._cache_time = 0
    
    @classmethod
    def _is_valid(cls) -> bool:
        """
        检查缓存是否有效
        
        Returns:
            bool: 如果缓存存在且未过期返回 True
        """
        if cls._cache is None:
            return False
        
        # 检查是否超过 TTL
        elapsed = time.time() - cls._cache_time
        return elapsed < cls.CACHE_TTL
    
    @classmethod
    def get_cache_info(cls) -> Dict[str, Any]:
        """
        获取缓存信息（用于调试和监控）
        
        Returns:
            Dict: 包含缓存状态、剩余时间等信息
        """
        with cls._lock:
            if cls._cache is None:
                return {
                    'cached': False,
                    'age': 0,
                    'remaining_ttl': 0
                }
            
            age = time.time() - cls._cache_time
            remaining = max(0, cls.CACHE_TTL - age)
            
            return {
                'cached': True,
                'age': round(age, 2),
                'remaining_ttl': round(remaining, 2),
                'total_ttl': cls.CACHE_TTL,
                'is_valid': cls._is_valid()
            }
    
    @classmethod
    def set_ttl(cls, ttl_seconds: int) -> None:
        """
        动态设置 TTL（主要用于测试）
        
        Args:
            ttl_seconds: 新的 TTL 值（秒）
        """
        cls.CACHE_TTL = ttl_seconds


# 全局配置缓存实例（方便直接使用）
config_cache = ConfigCache

