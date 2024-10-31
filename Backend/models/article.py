from flask_mongoengine import MongoEngine
from datetime import datetime

db = MongoEngine()

class DailyNewsletter(db.Document):
    date = db.DateTimeField(required=True, unique=True)
    sections = db.ListField(db.DictField())
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'daily_newsletters',
        'indexes': ['date'],
        'ordering': ['-date']
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'date': self.date.strftime('%Y-%m-%d'),
            'sections': self.sections,
            'created_at': self.created_at.isoformat()
        }
