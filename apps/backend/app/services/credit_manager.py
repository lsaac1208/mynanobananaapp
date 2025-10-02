"""
用户次数管理服务
"""
from flask import current_app
from app import db
from app.models.user import User
from app.models.creation import Creation
from typing import Dict, Any, Optional


class CreditManagerService:
    """用户次数管理服务"""

    @staticmethod
    def check_user_credits(user_id: int, required_credits: int = 1) -> Dict[str, Any]:
        """检查用户是否有足够次数"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found',
                    'has_credits': False,
                    'current_credits': 0
                }

            has_credits = user.credits >= required_credits

            return {
                'success': True,
                'has_credits': has_credits,
                'current_credits': user.credits,
                'required_credits': required_credits
            }

        except Exception as e:
            current_app.logger.error(f"Error checking user credits: {str(e)}")
            return {
                'success': False,
                'error': 'Database error',
                'has_credits': False,
                'current_credits': 0
            }

    @staticmethod
    def consume_credits(user_id: int, credits_to_consume: int = 1) -> Dict[str, Any]:
        """消费用户次数"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found',
                    'credits_consumed': 0,
                    'remaining_credits': 0
                }

            if user.credits < credits_to_consume:
                return {
                    'success': False,
                    'error': 'Insufficient credits',
                    'credits_consumed': 0,
                    'remaining_credits': user.credits
                }

            # 扣除次数
            user.credits -= credits_to_consume
            db.session.commit()

            return {
                'success': True,
                'credits_consumed': credits_to_consume,
                'remaining_credits': user.credits
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error consuming credits: {str(e)}")
            return {
                'success': False,
                'error': 'Database error',
                'credits_consumed': 0,
                'remaining_credits': 0
            }

    @staticmethod
    def add_credits(user_id: int, credits_to_add: int) -> Dict[str, Any]:
        """增加用户次数（管理员功能）"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found',
                    'credits_added': 0,
                    'total_credits': 0
                }

            user.credits += credits_to_add
            db.session.commit()

            return {
                'success': True,
                'credits_added': credits_to_add,
                'total_credits': user.credits
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding credits: {str(e)}")
            return {
                'success': False,
                'error': 'Database error',
                'credits_added': 0,
                'total_credits': 0
            }

    @staticmethod
    def refund_credits(user_id: int, credits_to_refund: int, reason: str = '') -> Dict[str, Any]:
        """退还用户次数（生成失败时）"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found',
                    'credits_refunded': 0,
                    'total_credits': 0
                }

            user.credits += credits_to_refund
            db.session.commit()

            current_app.logger.info(f"Refunded {credits_to_refund} credits to user {user_id}. Reason: {reason}")

            return {
                'success': True,
                'credits_refunded': credits_to_refund,
                'total_credits': user.credits,
                'reason': reason
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error refunding credits: {str(e)}")
            return {
                'success': False,
                'error': 'Database error',
                'credits_refunded': 0,
                'total_credits': 0
            }

    @staticmethod
    def get_user_credit_history(user_id: int, limit: int = 10) -> Dict[str, Any]:
        """获取用户次数使用历史"""
        try:
            # 获取用户的生成记录
            creations = Creation.query.filter_by(user_id=user_id).order_by(
                Creation.created_at.desc()
            ).limit(limit).all()

            history = []
            for creation in creations:
                history.append({
                    'id': creation.id,
                    'type': 'consume',
                    'credits_used': 1,  # 每次生成消费1个次数
                    'prompt': creation.prompt[:100] + '...' if len(creation.prompt) > 100 else creation.prompt,
                    'model_used': creation.model_used,
                    'created_at': creation.created_at.isoformat()
                })

            # 获取当前用户信息
            user = User.query.get(user_id)
            current_credits = user.credits if user else 0

            return {
                'success': True,
                'current_credits': current_credits,
                'history': history,
                'total_records': len(history)
            }

        except Exception as e:
            current_app.logger.error(f"Error getting credit history: {str(e)}")
            return {
                'success': False,
                'error': 'Database error',
                'current_credits': 0,
                'history': [],
                'total_records': 0
            }


# 辅助函数
def check_credits_decorator(required_credits: int = 1):
    """装饰器：检查用户次数"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 这里需要从请求中获取用户ID
            # 实际使用时需要配合JWT认证
            pass
        return wrapper
    return decorator