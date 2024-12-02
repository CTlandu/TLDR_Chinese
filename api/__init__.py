from flask import Flask
from flask_mongoengine import MongoEngine
from flaskext.markdown import Markdown
from config import Config
import logging
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = MongoEngine()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False  # 添加这行
    
    # 允许所有来源的 CORS 请求
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173", 
                "https://tldr-chinese-frontend.onrender.com",
                "https://tldr-chinese-backend.onrender.com",
                "https://www.tldrnewsletter.cn",
                "https://tldrnewsletter.cn",
                "http://www.tldrnewsletter.cn",
                "http://tldrnewsletter.cn"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True,
            "max_age": 600
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
    
    # 初始化 Limiter
    limiter.init_app(app)
    
    # 注册蓝图
    from .routes import bp
    app.register_blueprint(bp)
    
    return app
