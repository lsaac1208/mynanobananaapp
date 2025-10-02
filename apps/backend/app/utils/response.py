"""
统一API响应格式工具
"""
from flask import jsonify
from typing import Any, Optional, Dict


class APIResponse:
    """统一API响应格式"""

    @staticmethod
    def success(
        data: Optional[Any] = None,
        message: str = "操作成功",
        status_code: int = 200
    ):
        """成功响应"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code

    @staticmethod
    def error(
        message: str = "操作失败",
        error_code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict] = None
    ):
        """错误响应"""
        response = {
            'success': False,
            'error': message
        }
        if error_code:
            response['error_code'] = error_code
        if details:
            response['details'] = details
        return jsonify(response), status_code

    @staticmethod
    def created(data: Any, message: str = "创建成功"):
        """资源创建成功响应"""
        return APIResponse.success(data, message, 201)

    @staticmethod
    def no_content(message: str = "操作成功"):
        """无内容响应"""
        return APIResponse.success(None, message, 204)

    @staticmethod
    def bad_request(message: str = "请求参数错误", details: Optional[Dict] = None):
        """400 错误请求"""
        return APIResponse.error(message, "BAD_REQUEST", 400, details)

    @staticmethod
    def unauthorized(message: str = "未授权访问"):
        """401 未授权"""
        return APIResponse.error(message, "UNAUTHORIZED", 401)

    @staticmethod
    def forbidden(message: str = "禁止访问"):
        """403 禁止"""
        return APIResponse.error(message, "FORBIDDEN", 403)

    @staticmethod
    def not_found(message: str = "资源不存在"):
        """404 未找到"""
        return APIResponse.error(message, "NOT_FOUND", 404)

    @staticmethod
    def conflict(message: str = "资源冲突"):
        """409 冲突"""
        return APIResponse.error(message, "CONFLICT", 409)

    @staticmethod
    def too_many_requests(message: str = "请求过于频繁"):
        """429 请求过多"""
        return APIResponse.error(message, "TOO_MANY_REQUESTS", 429)

    @staticmethod
    def internal_error(message: str = "服务器内部错误"):
        """500 服务器错误"""
        return APIResponse.error(message, "INTERNAL_ERROR", 500)


# 便捷函数
def success_response(*args, **kwargs):
    """成功响应便捷函数"""
    return APIResponse.success(*args, **kwargs)


def error_response(*args, **kwargs):
    """错误响应便捷函数"""
    return APIResponse.error(*args, **kwargs)