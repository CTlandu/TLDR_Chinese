import os
from pathlib import Path
import logging
import dns.resolver
from pymongo import MongoClient
from api import create_app
from config import get_config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_mongodb_dns():
    """设置 MongoDB DNS 解析器"""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '8.8.4.4']
    dns.resolver.default_resolver = resolver

def get_app_config():
    env = os.environ.get('FLASK_ENV', 'development')
    logger.info(f"Running in {env} environment")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # 设置 MongoDB DNS
    setup_mongodb_dns()
    
    try:
        config = get_config()
        
        # 验证配置
        logger.info(f"MongoDB URI: {config.MONGODB_SETTINGS['host']}")
        
        # 测试连接
        client = MongoClient(
            config.MONGODB_SETTINGS['host'],
            serverSelectionTimeoutMS=5000,
            ssl=True,
            tlsInsecure=True,
            directConnection=False,
            connect=True
        )
        client.admin.command('ping')
        logger.info("MongoDB connection test successful!")
        
        return config
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        raise

try:
    config = get_app_config()
    app = create_app(config)
except Exception as e:
    logger.error(f"Failed to create app: {str(e)}")
    raise

if __name__ == '__main__':
    app.run(debug=config.DEBUG, use_reloader=False)