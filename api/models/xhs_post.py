from api import db
from datetime import datetime

STATUS_DRAFTED = 'drafted'
STATUS_PUBLISHED = 'published'
STATUS_DISCARDED = 'discarded'

STATUSES = (STATUS_DRAFTED, STATUS_PUBLISHED, STATUS_DISCARDED)


class XhsPost(db.Document):
    """一条新闻的小红书出稿记录。

    生成即写入（drafted），无论最后有没有发出去。去重按 source_url 做，
    所以同一条新闻只会出一次稿，不会在审核页反复出现。
    """

    source_url = db.StringField(required=True, unique=True)
    source_date = db.DateField(required=True)
    source_title = db.StringField()

    title = db.StringField()
    body = db.StringField()
    tags = db.ListField(db.StringField())
    output_dir = db.StringField()

    status = db.StringField(required=True, default=STATUS_DRAFTED, choices=STATUSES)
    created_at = db.DateTimeField(default=datetime.utcnow)
    published_at = db.DateTimeField()

    meta = {
        'collection': 'xhs_posts',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['source_url'], 'unique': True},
            'source_date',
            'status',
        ]
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'source_url': self.source_url,
            'source_date': self.source_date.strftime('%Y-%m-%d'),
            'title': self.title,
            'body': self.body,
            'tags': list(self.tags),
            'output_dir': self.output_dir,
            'status': self.status,
        }
