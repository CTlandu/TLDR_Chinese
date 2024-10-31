from flask_mongoengine import MongoEngine
from datetime import datetime

db = MongoEngine()

class Article(db.Document):
    # 定义字段
    date = db.DateTimeField(required=True)
    section = db.StringField(required=True)
    title = db.StringField(required=True)
    title_zh = db.StringField(required=True)
    content = db.StringField(required=True)
    content_zh = db.StringField(required=True)
    url = db.StringField()
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    # 元数据
    meta = {
        'collection': 'articles',  # 集合名称
        'indexes': [
            'date',  # 创建日期索引
            ('date', 'section')  # 复合索引
        ],
        'ordering': ['-date']  # 默认按日期降序排序
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'date': self.date.strftime('%Y-%m-%d'),
            'section': self.section,
            'title': self.title,
            'title_zh': self.title_zh,
            'content': self.content,
            'content_zh': self.content_zh,
            'url': self.url,
            'created_at': self.created_at.isoformat()
        }
