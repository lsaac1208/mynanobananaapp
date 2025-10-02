"""
画廊相关视图
"""
from flask import Blueprint, jsonify

gallery_bp = Blueprint('gallery', __name__)


@gallery_bp.route('/gallery', methods=['GET'])
def get_gallery():
    """获取用户画廊 - 开发中"""
    return jsonify({'message': '画廊功能开发中...'}), 501