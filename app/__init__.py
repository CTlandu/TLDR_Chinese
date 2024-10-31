from flask import Flask
from config import Config
import markdown
import bleach

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'a', 'ul', 'ol', 'li', 'code', 
            'pre', 'img', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'sup', 'sub', 'b', 'i', 'small', 'mark'
        ]
        
        allowed_attrs = {
            '*': ['class', 'style', 'id'],
            'a': ['href', 'rel', 'target', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan', 'scope']
        }
        
        html = markdown.markdown(text, extensions=['extra', 'tables'])
        clean_html = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True,
            protocols=['http', 'https', 'mailto']
        )
        return clean_html
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app 