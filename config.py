import os
from dotenv import load_dotenv


# 根据环境加载对应的 .env 文件
env = os.environ.get('FLASK_ENV', 'development')
env_file = f'.env.{env}'

# 如果环境特定的 .env 文件存在就加载它
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    # 否则尝试加载默认的 .env 文件
    load_dotenv()

class Config:
    DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
    
    # 注释掉或删除代理设置
    # if os.environ.get('HTTPS_PROXY'):
    #     proxy = os.environ.get('HTTPS_PROXY')
    #     os.environ['PYMONGO_PROXY_URI'] = proxy
    
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
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    def __init__(self):
        # 确保在初始化时重新获取环境变量
        self.MONGODB_SETTINGS = {
            'host': os.environ.get('MONGODB_URI'),
            'db': 'tldrchinese',
            'connect': False,
            'authentication_source': 'admin',
            'serverSelectionTimeoutMS': 30000,
            'ssl': True,
            'tlsInsecure': True
        }
        
        # 如果没有 MongoDB URI，抛出错误
        if not self.MONGODB_SETTINGS['host']:
            raise ValueError("MongoDB URI is not configured")

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False