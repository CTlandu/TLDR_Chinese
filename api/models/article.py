from api import db
from datetime import datetime

class DailyNewsletter(db.Document):
    # date = db.DateTimeField(required=True, unique=True)
    date = db.DateField(required=True, unique=True)  # 只存储日期，不存储时间
    sections = db.ListField(db.DictField())
    title = db.StringField(default="<太长不看>今日科技要闻速递 🚀")
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'newsletters',
        'ordering': ['-date'],
        'indexes': [
            'date'
        ]
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'date': self.date.strftime('%Y-%m-%d'),
            'sections': self.sections,
            'created_at': self.created_at.isoformat()
        }

class Article(db.EmbeddedDocument):
    title = db.StringField(required=True)
    title_en = db.StringField(required=True)
    content = db.StringField(required=True)
    content_en = db.StringField(required=True)
    url = db.StringField(required=True)
    image_url = db.StringField()
    section = db.StringField(required=True)
