import os
from api import create_app
from config import DevelopmentConfig, ProductionConfig

env = os.environ.get('FLASK_ENV', 'development')
config = DevelopmentConfig if env == 'development' else ProductionConfig
app = create_app(config)

if __name__ == '__main__':
    app.run(debug=config.DEBUG)