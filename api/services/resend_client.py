import logging
import time
from urllib.parse import quote

import requests

API_BASE = 'https://api.resend.com'
PAGE_SIZE = 100
UNSUBSCRIBE_TOKEN_KEY = 'unsubscribe_token'


class ResendError(Exception):
    def __init__(self, status_code, body):
        super().__init__(f'Resend API {status_code}: {body}')
        self.status_code = status_code
        self.body = body


def _contact_path(email):
    return f"/contacts/{quote(email, safe='@')}"


class ResendClient:
    def __init__(self, api_key, segment_id, from_domain, min_interval=0.2, timeout=15):
        self.api_key = api_key
        self.segment_id = segment_id
        self.from_domain = from_domain
        # 默认限流是每个 team 10 req/s，批量同步时主动放慢，免得吃 429
        self.min_interval = min_interval
        self.timeout = timeout
        self._last_request_at = 0.0

    def _request(self, method, path, *, json=None, params=None, allow_404=False):
        wait = self._last_request_at + self.min_interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()

        response = requests.request(
            method,
            f'{API_BASE}{path}',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json=json,
            params=params,
            timeout=self.timeout,
        )
        if allow_404 and response.status_code == 404:
            return None
        if not response.ok:
            logging.error(f'Resend {method} {path} failed: {response.status_code} {response.text}')
            raise ResendError(response.status_code, response.text)
        return response.json()

    def _list_all(self, path):
        params = {'limit': PAGE_SIZE}
        while True:
            page = self._request('GET', path, params=params)
            yield from page['data']
            if not page.get('has_more') or not page['data']:
                return
            params = {'limit': PAGE_SIZE, 'after': page['data'][-1]['id']}

    def _sender(self, from_name, from_local):
        return f'{from_name} <{from_local}@{self.from_domain}>'

    def send_email(self, to, subject, html, from_name, from_local):
        data = self._request('POST', '/emails', json={
            'from': self._sender(from_name, from_local),
            'to': [to],
            'subject': subject,
            'html': html,
        })
        return data['id']

    def get_contact(self, email):
        return self._request('GET', _contact_path(email), allow_404=True)

    def create_contact(self, email, unsubscribe_token):
        data = self._request('POST', '/contacts', json={
            'email': email,
            'unsubscribed': False,
            'properties': {UNSUBSCRIBE_TOKEN_KEY: unsubscribe_token},
            'segments': [{'id': self.segment_id}],
        })
        return data['id']

    def update_contact(self, email, *, unsubscribed=None, unsubscribe_token=None):
        body = {}
        if unsubscribed is not None:
            body['unsubscribed'] = unsubscribed
        if unsubscribe_token is not None:
            body['properties'] = {UNSUBSCRIBE_TOKEN_KEY: unsubscribe_token}
        return self._request('PATCH', _contact_path(email), json=body)

    def ensure_in_segment(self, email):
        path = f'{_contact_path(email)}/segments'
        if any(segment['id'] == self.segment_id for segment in self._list_all(path)):
            return
        self._request('POST', f'{path}/{self.segment_id}')

    def subscribe_contact(self, email, unsubscribe_token):
        """确认订阅时调用：没有就新建；已有（比如退订后重订）就改回订阅、写 token、补进 segment。"""
        if self.get_contact(email) is None:
            self.create_contact(email, unsubscribe_token)
            return
        self.update_contact(email, unsubscribed=False, unsubscribe_token=unsubscribe_token)
        self.ensure_in_segment(email)

    def list_contacts(self):
        return [
            {'id': c['id'], 'email': c['email'], 'unsubscribed': c['unsubscribed']}
            for c in self._list_all('/contacts')
        ]

    def ensure_contact_property(self, key):
        """返回 True 表示这次新建了属性。"""
        if any(prop['key'] == key for prop in self._list_all('/contact-properties')):
            return False
        self._request('POST', '/contact-properties', json={'key': key, 'type': 'string'})
        return True

    def send_broadcast(self, subject, html, name, from_name, from_local):
        data = self._request('POST', '/broadcasts', json={
            'segment_id': self.segment_id,
            'from': self._sender(from_name, from_local),
            'subject': subject,
            'html': html,
            'name': name,
            'send': True,
        })
        return data['id']
