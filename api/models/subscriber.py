from api import db
from datetime import datetime

class Subscriber(db.Document):
    """订阅者模型"""
    email = db.EmailField(required=True, unique=True)
    confirmation_token = db.StringField(required=True)
    confirmed = db.BooleanField(default=False)
    subscribed_at = db.DateTimeField(default=datetime.utcnow)
    confirmed_at = db.DateTimeField()
    unsubscribed_at = db.DateTimeField()
    is_active = db.BooleanField(default=True)
    
    meta = {
        'collection': 'subscribers',
        'indexes': [
            'email',
            'confirmation_token',
            ('confirmed', 'is_active')  # 复合索引用于快速查询活跃订阅者
        ],
        'ordering': ['-subscribed_at']
    }
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': str(self.id),
            'email': self.email,
            'confirmed': self.confirmed,
            'subscribed_at': self.subscribed_at.isoformat() if self.subscribed_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_active_subscribers(cls):
        """获取所有已确认且活跃的订阅者"""
        return cls.objects(confirmed=True, is_active=True)
    
    def confirm_subscription(self):
        """确认订阅"""
        self.confirmed = True
        self.confirmed_at = datetime.utcnow()
        self.save()
    
    def unsubscribe(self):
        """退订"""
        self.is_active = False
        self.unsubscribed_at = datetime.utcnow()
        self.save()