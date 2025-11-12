"""
Vercel Serverless Function 入口文件
用于将 Flask 应用适配到 Vercel 的 serverless 环境
"""
import os
import sys
from pathlib import Path

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'

# 确保项目根目录在 Python 路径中
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# 导入 Flask 应用
from api import create_app
from config import get_config

# 初始化配置和应用
try:
    config = get_config()
    app = create_app(config)
except Exception as e:
    import logging
    logging.error(f"Failed to initialize Flask app: {str(e)}")
    raise

# Vercel 会调用这个 handler 函数
# 这是一个标准的 WSGI 应用包装器
def handler(environ, start_response):
    """
    Vercel serverless function handler
    将请求转发给 Flask 应用
    """
    return app(environ, start_response)

# 导出 app 供 Vercel 使用
# Vercel 可以识别 app 变量作为 WSGI 应用
__all__ = ['app', 'handler']

