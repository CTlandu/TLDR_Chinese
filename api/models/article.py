from api import db
from datetime import datetime

class DailyNewsletter(db.Document):
    date = db.DateTimeField(required=True, unique=True)
    sections = db.ListField(db.DictField())
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
