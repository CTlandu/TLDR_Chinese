import sys
from types import SimpleNamespace

from conftest import load_module

sync = load_module('api/services/subscriber_sync.py')


def _sub(email, confirmed=True, is_active=True):
    return {'email': email, 'confirmed': confirmed, 'is_active': is_active}


def _contact(email, unsubscribed=False):
    return {'id': f'id-{email}', 'email': email, 'unsubscribed': unsubscribed}


def test_resend_unsubscribed_marks_active_mongo_subscriber_inactive():
    plan = sync.plan_sync([_contact('a@x.com', unsubscribed=True)], [_sub('a@x.com')])

    assert plan.mark_inactive == ['a@x.com']
    assert plan.create_contacts == []
    assert plan.unsubscribe_contacts == []


def test_active_mongo_subscriber_missing_in_resend_gets_created():
    plan = sync.plan_sync([], [_sub('a@x.com')])

    assert plan.create_contacts == ['a@x.com']
    assert plan.mark_inactive == []


def test_resend_subscribed_but_not_active_in_mongo_gets_unsubscribed():
    contacts = [
        _contact('gone@x.com'),
        _contact('left@x.com'),
        _contact('pending@x.com'),
    ]
    subscribers = [
        _sub('left@x.com', is_active=False),
        _sub('pending@x.com', confirmed=False),
    ]

    plan = sync.plan_sync(contacts, subscribers)

    assert plan.unsubscribe_contacts == ['gone@x.com', 'left@x.com', 'pending@x.com']
    assert plan.mark_inactive == []
    assert plan.create_contacts == []


def test_email_comparison_ignores_case():
    plan = sync.plan_sync(
        [_contact('Reader@X.com'), _contact('Quit@X.com', unsubscribed=True)],
        [_sub('reader@x.com'), _sub('quit@x.com')],
    )

    assert plan.create_contacts == []
    assert plan.unsubscribe_contacts == []
    assert plan.mark_inactive == ['quit@x.com']


def test_unconfirmed_subscribers_are_not_pushed_to_resend():
    plan = sync.plan_sync([], [_sub('pending@x.com', confirmed=False)])

    assert plan.counts() == {'mark_inactive': 0, 'create_contacts': 0, 'unsubscribe_contacts': 0}


def test_consistent_state_produces_no_actions():
    contacts = [
        _contact('a@x.com'),
        _contact('b@x.com', unsubscribed=True),
    ]
    subscribers = [
        _sub('a@x.com'),
        _sub('b@x.com', is_active=False),
        _sub('c@x.com', confirmed=False),
    ]

    plan = sync.plan_sync(contacts, subscribers)

    assert plan.counts() == {'mark_inactive': 0, 'create_contacts': 0, 'unsubscribe_contacts': 0}


class FakeSubscriber:
    def __init__(self, email, confirmed=True, is_active=True, token=None):
        self.email = email
        self.confirmed = confirmed
        self.is_active = is_active
        self.token = token
        self.unsubscribed_with = None

    @property
    def is_subscribed(self):
        return self.confirmed and self.is_active

    def ensure_unsubscribe_token(self):
        if not self.token:
            self.token = f'tok-{self.email}'
        return self.token

    def unsubscribe(self, source, reasons=None, comment=''):
        self.is_active = False
        self.unsubscribed_with = source


class FakeClient:
    def __init__(self, contacts):
        self.contacts = contacts
        self.created = []
        self.updated = []

    def list_contacts(self):
        return self.contacts

    def create_contact(self, email, token):
        self.created.append((email, token))

    def update_contact(self, email, **kwargs):
        self.updated.append((email, kwargs))


def _install_fake_model(monkeypatch, subscribers):
    model = SimpleNamespace(Subscriber=SimpleNamespace(objects=lambda: subscribers))
    monkeypatch.setitem(sys.modules, 'api.models.subscriber', model)


def test_run_sync_executes_all_three_kinds_of_actions(monkeypatch):
    quitter = FakeSubscriber('quit@x.com')
    newcomer = FakeSubscriber('new@x.com')
    _install_fake_model(monkeypatch, [quitter, newcomer, FakeSubscriber('old@x.com', is_active=False)])
    client = FakeClient([_contact('quit@x.com', unsubscribed=True), _contact('old@x.com')])

    plan = sync.run_sync(client)

    assert quitter.unsubscribed_with == 'resend'
    assert client.created == [('new@x.com', 'tok-new@x.com')]
    assert client.updated == [('old@x.com', {'unsubscribed': True})]
    assert plan.counts() == {'mark_inactive': 1, 'create_contacts': 1, 'unsubscribe_contacts': 1}


def test_run_sync_dry_run_changes_nothing(monkeypatch):
    quitter = FakeSubscriber('quit@x.com')
    newcomer = FakeSubscriber('new@x.com')
    _install_fake_model(monkeypatch, [quitter, newcomer])
    client = FakeClient([_contact('quit@x.com', unsubscribed=True), _contact('stray@x.com')])

    plan = sync.run_sync(client, dry_run=True)

    assert plan.counts() == {'mark_inactive': 1, 'create_contacts': 1, 'unsubscribe_contacts': 1}
    assert quitter.is_active is True
    assert newcomer.token is None
    assert client.created == []
    assert client.updated == []
