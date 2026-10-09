"""把 Mongo 里的订阅者同步到 Resend contacts。

默认 dry-run，只打印会做什么；加 --apply 才真正执行。
上线前用生产库跑一次，把现有订阅者导进 Resend。
"""
import argparse
import sys
import os
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import create_app
from api.models.subscriber import Subscriber
from api.services.resend_client import ResendClient, UNSUBSCRIBE_TOKEN_KEY
from api.services.subscriber_sync import run_sync
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_plan(plan):
    sections = [
        ('Resend 已退订 → Mongo 标 inactive', plan.mark_inactive),
        ('Mongo 在订、Resend 没有 → 新建 contact', plan.create_contacts),
        ('Resend 在订、Mongo 不在订 → Resend 标退订', plan.unsubscribe_contacts),
    ]
    for title, emails in sections:
        print(f'{title}: {len(emails)}')
        for email in emails:
            print(f'  {email}')


def main():
    parser = argparse.ArgumentParser(description='同步 Mongo 订阅者到 Resend contacts')
    parser.add_argument('--apply', action='store_true', help='真正执行（默认只打印计划）')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        client = ResendClient(
            app.config['RESEND_API_KEY'],
            app.config['RESEND_SEGMENT_ID'],
            app.config['MAIL_FROM_DOMAIN'],
        )
        missing_token = Subscriber.objects(unsubscribe_token=None)

        if not args.apply:
            print(f'[dry-run] 缺 unsubscribe_token 的订阅者: {missing_token.count()}')
            print_plan(run_sync(client, dry_run=True))
            print('[dry-run] 没有做任何修改。确认无误后加 --apply 执行。')
            return

        if client.ensure_contact_property(UNSUBSCRIBE_TOKEN_KEY):
            logger.info(f'Created Resend contact property: {UNSUBSCRIBE_TOKEN_KEY}')

        # 先 list 出来再改，边遍历游标边改被查询的字段可能漏掉文档
        to_fill = list(missing_token)
        for subscriber in to_fill:
            subscriber.ensure_unsubscribe_token()
        logger.info(f'Filled unsubscribe_token for {len(to_fill)} subscribers')

        print_plan(run_sync(client))
        print('同步完成。')


if __name__ == '__main__':
    main()
