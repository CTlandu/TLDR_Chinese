from flask import Flask
from flask_mongoengine import MongoEngine
from flaskext.markdown import Markdown
from config import Config
import logging
from flask_cors import CORS
db = MongoEngine()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False  # 添加这行
    
    # 允许所有来源的 CORS 请求
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "https://tldr-chinese-frontend.onrender.com","https://tldr-chinese-backend.onrender.com"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    app.config.from_object(config_class)
    
    # 初始化 Markdown
    Markdown(app)
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 初始化数据库
        db.init_app(app)
        # 测试连接
        with app.app_context():
            db.connection.server_info()
        logging.info("Successfully connected to MongoDB")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {str(e)}")
        raise
    
    # 注册蓝图
    from .routes import bp
    app.register_blueprint(bp)
    
    return app
