from datetime import date
from types import SimpleNamespace

from conftest import load_module

newsletter_email = load_module('api/services/newsletter_email.py')


def _newsletter():
    return SimpleNamespace(
        date=date(2026, 10, 9),
        generated_title='今日标题',
        sections=[
            {
                'section': 'Big Tech & Startups',
                'articles': [
                    {
                        'title': '文章一',
                        'content': '摘要一',
                        'url': 'https://example.com/1',
                        'image_url': 'https://example.com/1.png',
                    },
                    {'title': '文章二', 'content': '摘要二', 'url': 'https://example.com/2'},
                ],
            }
        ],
    )


def test_footer_links_to_frontend_unsubscribe_page_with_contact_placeholder():
    html = newsletter_email.generate_newsletter_html(_newsletter(), 'https://www.tldrnewsletter.cn/')

    assert 'https://www.tldrnewsletter.cn/unsubscribe?token={{{contact.unsubscribe_token}}}' in html
    assert html.count('{{{contact.unsubscribe_token}}}') == 1
    assert html.count('{{{') == 1
    assert html.count('}}}') == 1


def test_no_mailgun_or_backend_unsubscribe_left():
    html = newsletter_email.generate_newsletter_html(_newsletter(), 'https://www.tldrnewsletter.cn')

    assert '%recipient' not in html
    assert '/api/unsubscribe' not in html


def test_body_still_renders_articles():
    html = newsletter_email.generate_newsletter_html(_newsletter(), 'https://www.tldrnewsletter.cn')

    assert '今日标题' in html
    assert '2026-10-09' in html
    assert '文章一' in html and '摘要二' in html
    assert 'https://example.com/1.png' in html
    assert html.count('阅读原文') == 2


def test_confirmation_email_contains_link_as_button_and_text():
    html = newsletter_email.confirmation_email_html('https://api.example.com/api/confirm/abc')

    assert html.count('https://api.example.com/api/confirm/abc') == 2
