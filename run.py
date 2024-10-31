from dotenv import load_dotenv
import os

# 根据环境加载对应的 .env 文件
env = os.environ.get('FLASK_ENV', 'development')
env_file = f'.env.{env}'
load_dotenv(env_file)

from api import create_app
from config import DevelopmentConfig, ProductionConfig

config = DevelopmentConfig if env == 'development' else ProductionConfig
app = create_app(config)

if __name__ == '__main__':
    app.run(debug=config.DEBUG)