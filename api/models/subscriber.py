from api import db
from datetime import datetime
import secrets

class Subscriber(db.Document):
    """订阅者模型"""
    email = db.EmailField(required=True, unique=True)
    confirmation_token = db.StringField(required=True)
    confirmed = db.BooleanField(default=False)
    subscribed_at = db.DateTimeField(default=datetime.utcnow)
    confirmed_at = db.DateTimeField()
    unsubscribed_at = db.DateTimeField()
    is_active = db.BooleanField(default=True)
    unsubscribe_token = db.StringField()
    
    meta = {
        'collection': 'subscribers',
        'indexes': [
            'email',
            'confirmation_token',
            'unsubscribe_token',
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
    
    @property
    def is_subscribed(self):
        return self.confirmed and self.is_active

    def confirm_subscription(self):
        """确认订阅"""
        self.confirmed = True
        self.confirmed_at = datetime.utcnow()
        self.save()
    
    def ensure_unsubscribe_token(self):
        """老数据没有 token，用到时再补"""
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(32)
            self.save()
        return self.unsubscribe_token

    def unsubscribe(self, source, reasons=None, comment=''):
        """退订，并记一条退订事件"""
        self.is_active = False
        self.unsubscribed_at = datetime.utcnow()
        self.save()
        UnsubscribeEvent(
            email=self.email,
            subscriber_id=self.id,
            subscribed_at=self.subscribed_at,
            confirmed_at=self.confirmed_at,
            unsubscribed_at=self.unsubscribed_at,
            source=source,
            reasons=reasons or [],
            comment=comment,
        ).save()


class UnsubscribeEvent(db.Document):
    """每次退订一条；同一个人退订、重订、再退订会留下多条"""
    email = db.StringField(required=True)
    subscriber_id = db.ObjectIdField()
    subscribed_at = db.DateTimeField()
    confirmed_at = db.DateTimeField()
    unsubscribed_at = db.DateTimeField(required=True)
    # page: 我们自己的退订页；resend: 群发前同步时发现 Resend 那边已退订（如邮箱客户端的一键退订）
    source = db.StringField(required=True, choices=('page', 'resend'))
    reasons = db.ListField(db.StringField())
    comment = db.StringField()

    meta = {
        'collection': 'unsubscribe_events',
        'indexes': ['email', '-unsubscribed_at'],
        'ordering': ['-unsubscribed_at']
    }
