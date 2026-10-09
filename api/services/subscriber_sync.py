from dataclasses import dataclass, field


@dataclass
class SyncPlan:
    # Resend 已退订、Mongo 还在订 → Mongo 标 inactive（Mongo 的 email）
    mark_inactive: list = field(default_factory=list)
    # Mongo 在订、Resend 没有这个 contact → 在 Resend 新建（Mongo 的 email）
    create_contacts: list = field(default_factory=list)
    # Resend 在订、Mongo 没这个人或不在订 → Resend 标退订（Resend 的 email）
    unsubscribe_contacts: list = field(default_factory=list)

    def counts(self):
        return {
            'mark_inactive': len(self.mark_inactive),
            'create_contacts': len(self.create_contacts),
            'unsubscribe_contacts': len(self.unsubscribe_contacts),
        }


def plan_sync(resend_contacts, subscribers):
    """resend_contacts: [{email, unsubscribed}]；subscribers: [{email, confirmed, is_active}]"""
    active = {}
    for sub in subscribers:
        if sub['confirmed'] and sub['is_active']:
            active.setdefault(sub['email'].lower(), sub['email'])

    in_resend = {}
    for contact in resend_contacts:
        in_resend[contact['email'].lower()] = contact

    plan = SyncPlan()
    for key, email in active.items():
        contact = in_resend.get(key)
        if contact is None:
            plan.create_contacts.append(email)
        elif contact['unsubscribed']:
            plan.mark_inactive.append(email)

    for contact in resend_contacts:
        if not contact['unsubscribed'] and contact['email'].lower() not in active:
            plan.unsubscribe_contacts.append(contact['email'])

    return plan


def run_sync(client, dry_run=False):
    # 放在函数里导入：模块顶层不碰 api 包，plan_sync 才能脱离 flask/mongo 单测
    from api.models.subscriber import Subscriber

    subscribers = list(Subscriber.objects())
    plan = plan_sync(
        client.list_contacts(),
        [{'email': s.email, 'confirmed': s.confirmed, 'is_active': s.is_active} for s in subscribers],
    )
    if dry_run:
        return plan

    active = {}
    for s in subscribers:
        if s.is_subscribed:
            active.setdefault(s.email.lower(), s)

    for email in plan.mark_inactive:
        active[email.lower()].unsubscribe(source='resend')
    for email in plan.create_contacts:
        subscriber = active[email.lower()]
        client.create_contact(subscriber.email, subscriber.ensure_unsubscribe_token())
    for email in plan.unsubscribe_contacts:
        client.update_contact(email, unsubscribed=True)

    return plan
