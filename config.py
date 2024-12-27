import os
from dotenv import load_dotenv

# 根据环境加载对应的 .env 文件
env = os.environ.get('FLASK_ENV', 'development')
env_file = f'.env.{env}'

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

class BaseConfig:
    DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
    DEBUG = False  # 默认关闭调试模式
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_URI'),
        'db': 'tldrchinese',
        'connect': False,
        'authentication_source': 'admin',
        'serverSelectionTimeoutMS': 30000,
        'ssl': True,
        'tlsInsecure': True
    }
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    FRONTEND_URL = os.environ.get('FRONTEND_URL')
    BACKEND_URL = os.environ.get('BACKEND_URL')
    NEWSLETTER_API_KEY = os.environ.get('NEWSLETTER_API_KEY')
    ERNIE_API_KEY = os.environ.get('ERNIE_API_KEY')  # 百度文心一言 API Key
    ERNIE_SECRET_KEY = os.environ.get('ERNIE_SECRET_KEY')  # 百度文心一言 Secret Key

class DevelopmentConfig(BaseConfig):
    DEBUG = True  # 开发环境开启调试模式
    
    def __init__(self):
        super().__init__()
        # 只在开发环境中设置代理，且仅当 USE_PROXY 为 true 时
        if os.environ.get('USE_PROXY', 'false').lower() == 'true':
            proxy = os.environ.get('HTTPS_PROXY')
            if proxy:
                self.HTTPS_PROXY = proxy
                os.environ['PYMONGO_PROXY_URI'] = proxy
                
class ProductionConfig(BaseConfig):
    DEBUG = False  # 生产环境关闭调试模式
    
    def __init__(self):
        super().__init__()
        # 生产环境不需要代理设置

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'development':
        return DevelopmentConfig()
    return ProductionConfig()

# 导出配置实例
Config = get_config()