import os
from api import create_app
from config import DevelopmentConfig, ProductionConfig
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    logger.info(f"Running in {env} environment")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    try:
        if env == 'development':
            config = DevelopmentConfig()
        else:
            config = ProductionConfig()
        
        # 验证配置
        logger.info(f"MongoDB URI: {config.MONGODB_SETTINGS['host']}")
        return config
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        raise

try:
    config = get_config()
    app = create_app(config)
except Exception as e:
    logger.error(f"Failed to create app: {str(e)}")
    raise

if __name__ == '__main__':
    app.run(debug=config.DEBUG)