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
config = get_config()
app = create_app(config)

# Vercel 会自动识别并使用这个 WSGI app

