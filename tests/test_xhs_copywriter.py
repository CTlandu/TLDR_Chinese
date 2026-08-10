import json

from conftest import FakeDeepSeekClient, load_module

cw = load_module('api/services/xhs_copywriter.py')


ARTICLE = {
    'url': 'https://a.example/1',
    'title': 'Apple ships new silicon',
    'content': '一段足够长的新闻正文内容。' * 10,
}


def _note(title='标题正好合规', body=None, cards=None, tags=None, cover_hook='封面钩子'):
    return {
        'title': title,
        'cover_hook': cover_hook,
        'body': body if body is not None else '第一段正文。\n\n第二段正文。\n\n第三段正文。',
        'cards': cards if cards is not None else ['卡片一', '卡片二'],
        'tags': tags if tags is not None else ['科技', 'AI', '数码'],
    }


def _service(client):
    return cw.XhsCopywriterService(api_key='unused', client=client)


def test_oversized_title_triggers_rewrite_and_compliant_rewrite_is_used():
    first = _note(title='这是一个整整二十五个字符长度的超长标题啊啊')
    second = _note(title='压缩后的合规标题')
    assert len(first['title']) > cw.TITLE_TARGET

    client = FakeDeepSeekClient(contents=[json.dumps(first), json.dumps(second)])
    note = _service(client).generate_note(ARTICLE)

    assert len(client.calls) == 2
    assert note['title'] == '压缩后的合规标题'


def test_still_oversized_after_rewrite_is_hard_truncated_without_raising():
    too_long = _note(title='一二三四五六七八九十一二三四五六七八九十')
    client = FakeDeepSeekClient(contents=[json.dumps(too_long), json.dumps(too_long)])

    note = _service(client).generate_note(ARTICLE)

    assert note is not None
    assert len(note['title']) == cw.TITLE_TARGET


def test_body_over_target_triggers_rewrite_even_when_under_hard_limit():
    long_body = '正' * 990
    assert cw.BODY_TARGET < len(long_body) < cw.BODY_LIMIT

    first = _note(body=long_body)
    second = _note(body='压缩后的正文。')
    client = FakeDeepSeekClient(contents=[json.dumps(first), json.dumps(second)])

    note = _service(client).generate_note(ARTICLE)

    assert len(client.calls) == 2
    assert note['body'] == '压缩后的正文。'


def test_too_many_tags_are_trimmed_to_max():
    client = FakeDeepSeekClient(
        content=json.dumps(_note(tags=[f'标签{i}' for i in range(cw.TAG_MAX + 4)]))
    )

    note = _service(client).generate_note(ARTICLE)

    assert len(note['tags']) == cw.TAG_MAX


def test_single_tag_warns_but_does_not_block(caplog):
    client = FakeDeepSeekClient(content=json.dumps(_note(tags=['只有一个'])))

    note = _service(client).generate_note(ARTICLE)

    assert note is not None
    assert note['tags'] == ['只有一个']


def test_tags_are_stripped_of_hash_and_deduped():
    client = FakeDeepSeekClient(
        content=json.dumps(_note(tags=['#科技', '科技', '#AI', 'AI ']))
    )

    note = _service(client).generate_note(ARTICLE)

    assert note['tags'] == ['科技', 'AI']


def test_char_counting_treats_cjk_and_latin_equally():
    assert len('中文中文中文') == 6
    assert len('abcdef') == 6

    mixed = '中文abc' * 4          # 20 字符，超过 TITLE_TARGET
    assert len(mixed) == 20
    assert cw.over_limit(_note(title=mixed)) is not None
    assert cw.over_limit(_note(title=mixed[:cw.TITLE_TARGET])) is None


def test_api_exception_returns_none():
    client = FakeDeepSeekClient(error=RuntimeError('timeout'))

    assert _service(client).generate_note(ARTICLE) is None


def test_unparseable_response_returns_none():
    client = FakeDeepSeekClient(content='模型今天不想输出 JSON')

    assert _service(client).generate_note(ARTICLE) is None


def test_empty_title_returns_none():
    client = FakeDeepSeekClient(content=json.dumps(_note(title='')))

    assert _service(client).generate_note(ARTICLE) is None


def test_markdown_fenced_response_is_parsed():
    payload = json.dumps(_note())
    client = FakeDeepSeekClient(content=f"```json\n{payload}\n```")

    note = _service(client).generate_note(ARTICLE)

    assert note['title'] == '标题正好合规'


def test_too_few_cards_are_resplit_from_body():
    client = FakeDeepSeekClient(content=json.dumps(_note(cards=['只有一张'])))

    note = _service(client).generate_note(ARTICLE)

    assert len(note['cards']) >= cw.CARD_MIN
    assert ''.join(note['cards']).replace('\n', '')


def test_too_many_cards_are_capped():
    client = FakeDeepSeekClient(
        content=json.dumps(_note(cards=[f'卡片{i}' for i in range(6)]))
    )

    note = _service(client).generate_note(ARTICLE)

    assert len(note['cards']) == cw.CARD_MAX


def test_missing_cover_hook_falls_back_to_title():
    client = FakeDeepSeekClient(content=json.dumps(_note(cover_hook='')))

    note = _service(client).generate_note(ARTICLE)

    assert note['cover_hook'] == note['title']


def test_compliant_note_makes_only_one_api_call():
    client = FakeDeepSeekClient(content=json.dumps(_note()))

    _service(client).generate_note(ARTICLE)

    assert len(client.calls) == 1
