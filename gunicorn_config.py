import os

class Config:
    DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_URI'),
        'db': 'tldrchinese',
        'connect': False,
        'authentication_source': 'admin'
    }

class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        'host': 'mongodb://localhost:27017',
        'db': 'tldrchinese_dev'
    }

class ProductionConfig(Config):
    DEBUG = False