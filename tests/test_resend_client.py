import json
from types import SimpleNamespace

import pytest

from conftest import load_module

resend = load_module('api/services/resend_client.py')


class FakeResponse:
    def __init__(self, data=None, status=200, text=None):
        self.status_code = status
        self._data = data
        self.text = text if text is not None else json.dumps(data)

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._data


@pytest.fixture
def http(monkeypatch):
    calls = []
    responses = []

    def fake_request(method, url, **kwargs):
        calls.append(SimpleNamespace(method=method, url=url, **kwargs))
        return responses.pop(0)

    monkeypatch.setattr(resend.requests, 'request', fake_request)
    return SimpleNamespace(calls=calls, responses=responses)


def _client():
    return resend.ResendClient('re_test', 'seg_123', 'tldrnewsletter.cn', min_interval=0)


def test_send_email_posts_to_emails_with_bearer_auth(http):
    http.responses.append(FakeResponse({'id': 'email_1'}))

    email_id = _client().send_email(
        'reader@example.com', '确认订阅', '<p>hi</p>',
        from_name='【太长不看】科技日推', from_local='confirm',
    )

    assert email_id == 'email_1'
    call = http.calls[0]
    assert (call.method, call.url) == ('POST', 'https://api.resend.com/emails')
    assert call.headers['Authorization'] == 'Bearer re_test'
    assert call.json == {
        'from': '【太长不看】科技日推 <confirm@tldrnewsletter.cn>',
        'to': ['reader@example.com'],
        'subject': '确认订阅',
        'html': '<p>hi</p>',
    }


def test_create_contact_sets_token_property_and_segment(http):
    http.responses.append(FakeResponse({'object': 'contact', 'id': 'c1'}))

    contact_id = _client().create_contact('reader@example.com', 'tok-abc')

    assert contact_id == 'c1'
    call = http.calls[0]
    assert (call.method, call.url) == ('POST', 'https://api.resend.com/contacts')
    assert call.json == {
        'email': 'reader@example.com',
        'unsubscribed': False,
        'properties': {'unsubscribe_token': 'tok-abc'},
        'segments': [{'id': 'seg_123'}],
    }


def test_update_contact_by_email_only_sends_given_fields(http):
    http.responses.append(FakeResponse({'object': 'contact', 'id': 'c1'}))

    _client().update_contact('a+b@example.com', unsubscribed=True)

    call = http.calls[0]
    assert call.method == 'PATCH'
    assert call.url == 'https://api.resend.com/contacts/a%2Bb@example.com'
    assert call.json == {'unsubscribed': True}


def test_update_contact_can_write_token(http):
    http.responses.append(FakeResponse({'object': 'contact', 'id': 'c1'}))

    _client().update_contact('a@example.com', unsubscribed=False, unsubscribe_token='tok')

    assert http.calls[0].json == {
        'unsubscribed': False,
        'properties': {'unsubscribe_token': 'tok'},
    }


def test_list_contacts_follows_after_cursor_until_has_more_is_false(http):
    http.responses.extend([
        FakeResponse({
            'object': 'list',
            'has_more': True,
            'data': [
                {'id': 'c1', 'email': 'a@x.com', 'unsubscribed': False, 'first_name': 'A'},
                {'id': 'c2', 'email': 'b@x.com', 'unsubscribed': True},
            ],
        }),
        FakeResponse({
            'object': 'list',
            'has_more': False,
            'data': [{'id': 'c3', 'email': 'c@x.com', 'unsubscribed': False}],
        }),
    ])

    contacts = _client().list_contacts()

    assert contacts == [
        {'id': 'c1', 'email': 'a@x.com', 'unsubscribed': False},
        {'id': 'c2', 'email': 'b@x.com', 'unsubscribed': True},
        {'id': 'c3', 'email': 'c@x.com', 'unsubscribed': False},
    ]
    assert [c.url for c in http.calls] == ['https://api.resend.com/contacts'] * 2
    assert http.calls[0].params == {'limit': 100}
    assert http.calls[1].params == {'limit': 100, 'after': 'c2'}


def test_ensure_contact_property_is_noop_when_key_exists(http):
    http.responses.append(FakeResponse({
        'object': 'list',
        'has_more': False,
        'data': [{'id': 'p1', 'key': 'unsubscribe_token', 'type': 'string'}],
    }))

    assert _client().ensure_contact_property('unsubscribe_token') is False
    assert len(http.calls) == 1
    assert http.calls[0].url == 'https://api.resend.com/contact-properties'


def test_ensure_contact_property_creates_string_property_when_missing(http):
    http.responses.extend([
        FakeResponse({'object': 'list', 'has_more': False, 'data': []}),
        FakeResponse({'object': 'contact_property', 'id': 'p1'}),
    ])

    assert _client().ensure_contact_property('unsubscribe_token') is True
    create = http.calls[1]
    assert (create.method, create.url) == ('POST', 'https://api.resend.com/contact-properties')
    assert create.json == {'key': 'unsubscribe_token', 'type': 'string'}


def test_send_broadcast_creates_and_sends_to_segment(http):
    http.responses.append(FakeResponse({'object': 'broadcast', 'id': 'b1'}))

    broadcast_id = _client().send_broadcast(
        '[标题] 2026-10-09', '<p>body</p>', name='TLDR 2026-10-09',
        from_name='太长不看 | 科技日推', from_local='newsletter',
    )

    assert broadcast_id == 'b1'
    call = http.calls[0]
    assert (call.method, call.url) == ('POST', 'https://api.resend.com/broadcasts')
    assert call.json == {
        'segment_id': 'seg_123',
        'from': '太长不看 | 科技日推 <newsletter@tldrnewsletter.cn>',
        'subject': '[标题] 2026-10-09',
        'html': '<p>body</p>',
        'name': 'TLDR 2026-10-09',
        'send': True,
    }
    assert 'audience_id' not in call.json


def test_non_2xx_raises_with_status_and_body(http, caplog):
    http.responses.append(FakeResponse(status=422, text='{"name":"validation_error"}'))

    with pytest.raises(resend.ResendError) as excinfo:
        _client().send_email('a@x.com', 's', 'h', from_name='n', from_local='l')

    assert excinfo.value.status_code == 422
    assert 'validation_error' in excinfo.value.body
    assert 'validation_error' in caplog.text


def test_subscribe_contact_creates_when_contact_missing(http):
    http.responses.extend([
        FakeResponse(status=404, text='{"name":"not_found"}'),
        FakeResponse({'object': 'contact', 'id': 'c1'}),
    ])

    _client().subscribe_contact('new@x.com', 'tok')

    assert [(c.method, c.url) for c in http.calls] == [
        ('GET', 'https://api.resend.com/contacts/new@x.com'),
        ('POST', 'https://api.resend.com/contacts'),
    ]
    assert http.calls[1].json['segments'] == [{'id': 'seg_123'}]


def test_subscribe_contact_resubscribes_existing_and_adds_missing_segment(http):
    http.responses.extend([
        FakeResponse({'object': 'contact', 'id': 'c1', 'email': 'old@x.com', 'unsubscribed': True}),
        FakeResponse({'object': 'contact', 'id': 'c1'}),
        FakeResponse({'object': 'list', 'has_more': False, 'data': [{'id': 'other_seg'}]}),
        FakeResponse({'id': 'seg_123'}),
    ])

    _client().subscribe_contact('old@x.com', 'tok')

    assert [(c.method, c.url) for c in http.calls] == [
        ('GET', 'https://api.resend.com/contacts/old@x.com'),
        ('PATCH', 'https://api.resend.com/contacts/old@x.com'),
        ('GET', 'https://api.resend.com/contacts/old@x.com/segments'),
        ('POST', 'https://api.resend.com/contacts/old@x.com/segments/seg_123'),
    ]
    assert http.calls[1].json == {
        'unsubscribed': False,
        'properties': {'unsubscribe_token': 'tok'},
    }


def test_subscribe_contact_skips_segment_add_when_already_member(http):
    http.responses.extend([
        FakeResponse({'object': 'contact', 'id': 'c1', 'email': 'old@x.com', 'unsubscribed': True}),
        FakeResponse({'object': 'contact', 'id': 'c1'}),
        FakeResponse({'object': 'list', 'has_more': False, 'data': [{'id': 'seg_123'}]}),
    ])

    _client().subscribe_contact('old@x.com', 'tok')

    assert len(http.calls) == 3
    assert http.calls[-1].method == 'GET'


def test_requests_are_spaced_by_min_interval(http, monkeypatch):
    sleeps = []
    monkeypatch.setattr(resend.time, 'monotonic', lambda: 100.0)
    monkeypatch.setattr(resend.time, 'sleep', sleeps.append)
    http.responses.extend([FakeResponse({'id': 'e1'}), FakeResponse({'id': 'e2'})])
    client = resend.ResendClient('re_test', 'seg_123', 'tldrnewsletter.cn', min_interval=0.2)

    client.send_email('a@x.com', 's', 'h', from_name='n', from_local='l')
    client.send_email('b@x.com', 's', 'h', from_name='n', from_local='l')

    assert sleeps == [pytest.approx(0.2)]
