"""
WSGI应用入口点
用于Gunicorn等WSGI服务器启动
解决app.py与app/包的命名冲突问题
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import create_app

# 创建应用实例
application = create_app()

# 为了兼容性，同时导出app
app = application

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

