import os

class Config:
    DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
    
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_URI'),
        'db': 'tldrchinese',
        'connect': False,
        'authentication_source': 'admin'
    }