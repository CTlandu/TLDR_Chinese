import struct
import zlib
from pathlib import Path

import pytest
from conftest import load_module

pipeline = load_module('scripts/xhs/run_daily.py')


def make_png(width=8, height=8):
    def chunk(tag, data):
        body = tag + data
        return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    raw = b''.join(b'\x00' + b'\xe8\x50\x3a' * width for _ in range(height))
    return (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', zlib.compress(raw))
        + chunk(b'IEND', b'')
    )


def articles(n):
    return [
        {
            'url': f'https://a.example/{i}',
            'title': f'第 {i} 条新闻',
            'content': '正文内容',
            'image_url': None,
        }
        for i in range(1, n + 1)
    ]


class FakeScorer:
    """按输入顺序倒序打分，这样排名和输入顺序不同，能验证 join 逻辑真的生效。"""

    def score_articles(self, items):
        return [
            {'url': a['url'], 'score': float(len(items) - i), 'reason': f'理由 {i}'}
            for i, a in enumerate(items)
        ]


class FakeCopywriter:
    def __init__(self, fail_urls=()):
        self.fail_urls = set(fail_urls)

    def generate_note(self, article):
        if article['url'] in self.fail_urls:
            return None
        return {
            'title': f"{article['title']}的标题",
            'cover_hook': '钩子',
            'body': '正文段落一。\n正文段落二。',
            'cards': ['卡片一', '卡片二'],
            'tags': ['科技', 'AI', '数码'],
        }


def fake_render(note, out_dir, image_url=None, source=''):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i in range(1, len(note['cards']) + 2):
        path = out_dir / f'{i:02d}.png'
        path.write_bytes(make_png())
        paths.append(path)
    return paths


def exploding_render(fail_on):
    def _render(note, out_dir, image_url=None, source=''):
        if fail_on in note['title']:
            raise RuntimeError('浏览器崩了')
        return fake_render(note, out_dir, image_url, source)
    return _render


def run(items, tmp_path, copywriter=None, render_fn=fake_render, top_n=3):
    return pipeline.run_pipeline(
        items,
        FakeScorer(),
        copywriter or FakeCopywriter(),
        render_fn,
        tmp_path,
        '2026-08-10',
        top_n=top_n,
    )


# ---------- flatten ----------

def test_flatten_pulls_articles_from_every_section():
    sections = [
        {'section': 'Big Tech', 'articles': [{'url': 'u1'}, {'url': 'u2'}]},
        {'section': 'Science', 'articles': [{'url': 'u3'}]},
    ]

    flat = pipeline.flatten_sections(sections)

    assert [a['url'] for a in flat] == ['u1', 'u2', 'u3']
    assert flat[0]['section'] == 'Big Tech'


def test_flatten_skips_section_without_articles_key():
    sections = [{'section': '空版块'}, {'section': 'ok', 'articles': [{'url': 'u1'}]}]

    assert [a['url'] for a in pipeline.flatten_sections(sections)] == ['u1']


def test_flatten_tolerates_none_and_malformed_entries():
    assert pipeline.flatten_sections(None) == []
    assert pipeline.flatten_sections([None, 'garbage']) == []
    assert pipeline.flatten_sections([{'articles': [None, {'url': 'u1'}]}])[0]['url'] == 'u1'


# ---------- selection ----------

def test_selection_follows_score_order_not_input_order():
    items = articles(4)

    picked = pipeline.select_candidates(items, FakeScorer(), top_n=3)

    assert [p['article']['url'] for p in picked] == [
        'https://a.example/1',
        'https://a.example/2',
        'https://a.example/3',
    ]
    assert picked[0]['score'] > picked[1]['score']


def test_selection_drops_urls_that_have_no_matching_article():
    class GhostScorer:
        def score_articles(self, items):
            return [{'url': 'https://ghost.example/x', 'score': 99.0, 'reason': '幽灵'}] + \
                   FakeScorer().score_articles(items)

    picked = pipeline.select_candidates(articles(2), GhostScorer(), top_n=3)

    assert len(picked) == 2


# ---------- pipeline ----------

def test_fewer_available_than_requested_produces_actual_count(tmp_path):
    result = run(articles(2), tmp_path)
    page = pipeline.render_review_page(result, tmp_path / '2026-08-10' / 'review.html')

    assert len(result['candidates']) == 2
    assert result['requested'] == 3
    assert '今日候选 2 / 3 篇' in page.read_text(encoding='utf-8')


def test_no_articles_still_produces_an_explanatory_review_page(tmp_path):
    result = run([], tmp_path)
    page = pipeline.render_review_page(result, tmp_path / '2026-08-10' / 'review.html')
    html = page.read_text(encoding='utf-8')

    assert result['candidates'] == []
    assert result['notice'] is not None
    assert page.exists()
    assert 'notice' in html
    assert '没有可用的候选新闻' in html


def test_middle_candidate_failure_does_not_block_the_others(tmp_path):
    copywriter = FakeCopywriter(fail_urls=['https://a.example/2'])

    result = run(articles(3), tmp_path, copywriter=copywriter)

    assert [c['index'] for c in result['candidates']] == [1, 3]
    assert [f['index'] for f in result['failures']] == [2]
    assert result['failures'][0]['stage'] == '文案生成'


def test_render_failure_is_recorded_without_killing_the_run(tmp_path):
    result = run(articles(3), tmp_path, render_fn=exploding_render('第 2 条新闻'))

    assert [c['index'] for c in result['candidates']] == [1, 3]
    assert result['failures'][0]['stage'] == '出图'


def test_all_candidates_failing_sets_a_notice(tmp_path):
    copywriter = FakeCopywriter(fail_urls=[a['url'] for a in articles(3)])

    result = run(articles(3), tmp_path, copywriter=copywriter)

    assert result['candidates'] == []
    assert '全部生成失败' in result['notice']


def test_failures_are_listed_on_the_review_page(tmp_path):
    copywriter = FakeCopywriter(fail_urls=['https://a.example/2'])
    result = run(articles(3), tmp_path, copywriter=copywriter)

    html = pipeline.render_review_page(
        result, tmp_path / '2026-08-10' / 'review.html'
    ).read_text(encoding='utf-8')

    assert '第 02 篇在「文案生成」阶段失败' in html


def test_rerunning_the_same_day_overwrites_instead_of_duplicating(tmp_path):
    run(articles(3), tmp_path)
    run(articles(3), tmp_path)

    day_dir = tmp_path / '2026-08-10'
    assert sorted(p.name for p in day_dir.iterdir()) == ['01', '02', '03']
    assert len(list((day_dir / '01').glob('*.png'))) == 3


def test_note_json_is_written_alongside_the_images(tmp_path):
    result = run(articles(1), tmp_path)
    path = pipeline.write_note_json(result['candidates'][0])

    import json
    payload = json.loads(path.read_text(encoding='utf-8'))

    assert payload['title'].endswith('的标题')
    assert payload['images'] == ['01.png', '02.png', '03.png']
    assert payload['source_url'] == 'https://a.example/1'


# ---------- review page ----------

def test_over_limit_title_is_flagged_on_the_review_page(tmp_path):
    class LongTitleCopywriter(FakeCopywriter):
        def generate_note(self, article):
            note = super().generate_note(article)
            note['title'] = '一' * 25
            return note

    result = run(articles(1), tmp_path, copywriter=LongTitleCopywriter())
    html = pipeline.render_review_page(
        result, tmp_path / '2026-08-10' / 'review.html'
    ).read_text(encoding='utf-8')

    assert 'count over' in html
    assert '25 / 20' in html


def test_review_page_escapes_content(tmp_path):
    class InjectingCopywriter(FakeCopywriter):
        def generate_note(self, article):
            note = super().generate_note(article)
            note['body'] = '<script>alert(1)</script>'
            return note

    result = run(articles(1), tmp_path, copywriter=InjectingCopywriter())
    html = pipeline.render_review_page(
        result, tmp_path / '2026-08-10' / 'review.html'
    ).read_text(encoding='utf-8')

    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html


def test_no_unreplaced_placeholders_on_review_page(tmp_path):
    result = run(articles(2), tmp_path)
    html = pipeline.render_review_page(
        result, tmp_path / '2026-08-10' / 'review.html'
    ).read_text(encoding='utf-8')

    assert '{{' not in html


def test_source_label_is_passed_through_to_the_renderer(tmp_path):
    seen = []

    def recording_render(note, out_dir, image_url=None, source=''):
        seen.append(source)
        return fake_render(note, out_dir, image_url, source)

    run(articles(2), tmp_path, render_fn=recording_render)

    assert seen == ['a.example/1', 'a.example/2']


def test_card_label_is_readable_not_a_wall_of_base64():
    """图上的链接点不了，它的活儿是公信力。四百字符的 token 铺上去是反效果。"""
    url = (
        'https://www.bloomberg.com/news/articles/2026-08-06/what-is-openai-s-device'
        '?accessToken=' + 'eyJhbGciOiJIUzI1NiJ9' * 20
    )

    label = pipeline.source_label(url)

    assert label == 'bloomberg.com/news/articles/2026-08-06/what-is-openai-s-device'
    assert 'accessToken' not in label
    assert len(label) < 80


def test_body_keeps_the_paywall_unlocking_token():
    """accessToken / unlocked_article_code 是免付费墙的钥匙，不能当跟踪参数删掉。"""
    url = (
        'https://www.nytimes.com/2026/08/06/science/x.html'
        '?unlocked_article_code=1.3lA.pm4x&smid=url-share&utm_source=tldrnewsletter'
    )

    body = pipeline.append_source({'body': '正文。'}, url)['body']

    assert 'unlocked_article_code=1.3lA.pm4x' in body
    assert 'utm_source' not in body
    assert 'smid' not in body


def test_source_line_is_appended_to_the_body():
    url = 'https://spyglass.org/you-are-the-tokens/'
    note = pipeline.append_source({'body': '正文内容。'}, url)

    assert note['body'].endswith(f'来源：{url}')
    assert note['body'].startswith('正文内容。')


def test_source_line_is_not_appended_twice():
    url = 'https://spyglass.org/you-are-the-tokens/'
    once = pipeline.append_source({'body': '正文。'}, url)
    twice = pipeline.append_source(once, url)

    assert twice['body'].count(url) == 1


def test_append_source_is_a_noop_without_url():
    note = {'body': '正文。'}

    assert pipeline.append_source(note, '')['body'] == '正文。'


def test_attach_source_text_marks_unfetchable_articles_as_empty(monkeypatch):
    import article_fetcher

    monkeypatch.setattr(
        article_fetcher, 'fetch_article_text',
        lambda url, **kw: 'full english body' if 'ok' in url else None
    )

    items = [{'url': 'https://ok.example/1'}, {'url': 'https://paywall.example/2'}]
    pipeline.attach_source_text(items, workers=2)

    assert items[0]['source_text'] == 'full english body'
    assert items[1]['source_text'] == ''


# ---------- 会话接管模式（prepare / build） ----------

def test_prepared_scorer_replays_the_given_order():
    picks = [
        {'url': 'https://a.example/2', 'score': 9.1, 'reason': '第一'},
        {'url': 'https://a.example/1', 'score': 4.2, 'reason': '第二'},
    ]

    ranked = pipeline.PreparedScorer(picks).score_articles(articles(3))

    assert [r['url'] for r in ranked] == ['https://a.example/2', 'https://a.example/1']
    assert ranked[0]['score'] == 9.1


def test_prepared_copywriter_returns_none_for_unpicked_articles():
    picks = [{'url': 'https://a.example/1', 'note': {'title': 'T'}}]
    cw = pipeline.PreparedCopywriter(picks)

    assert cw.generate_note({'url': 'https://a.example/1'})['title'] == 'T'
    assert cw.generate_note({'url': 'https://a.example/9'}) is None


def test_prepared_copywriter_hands_out_copies_not_shared_state():
    picks = [{'url': 'https://a.example/1', 'note': {'title': 'T', 'tags': []}}]
    cw = pipeline.PreparedCopywriter(picks)

    first = cw.generate_note({'url': 'https://a.example/1'})
    first['title'] = '被改了'

    assert cw.generate_note({'url': 'https://a.example/1'})['title'] == 'T'


def test_handwritten_note_still_gets_length_enforced():
    note = pipeline.normalize_note({
        'title': '一' * 30,
        'body': '正文。',
        'cards': ['只有一张'],
        'tags': ['#科技', '科技', '#AI', 'a', 'b', 'c', 'd'],
    })

    assert len(note['title']) == 18
    assert len(note['cards']) >= 2
    assert len(note['tags']) <= 6
    assert '#' not in ''.join(note['tags'])
    assert note['cover_hook'] == note['title']


def test_output_dir_scan_collects_previously_drafted_urls(tmp_path):
    run(articles(2), tmp_path)
    for candidate in run(articles(2), tmp_path)['candidates']:
        pipeline.write_note_json(candidate)

    seen = pipeline.seen_urls_from_output(tmp_path)

    assert seen == {'https://a.example/1', 'https://a.example/2'}


def test_output_dir_scan_ignores_corrupt_note_files(tmp_path):
    broken = tmp_path / '2026-08-10' / '01'
    broken.mkdir(parents=True)
    (broken / 'note.json').write_text('{ not json', encoding='utf-8')

    assert pipeline.seen_urls_from_output(tmp_path) == set()


def test_public_api_fetch_flattens_and_warns_on_date_mismatch(monkeypatch, caplog):
    from types import SimpleNamespace

    payload = {
        'currentDate': '2026-08-07',
        'sections': [{'section': 'Tech', 'articles': [{'url': 'u1', 'title': 't1'}]}],
    }
    monkeypatch.setattr(
        pipeline.requests, 'get',
        lambda url, **kw: SimpleNamespace(
            status_code=200, json=lambda: payload, raise_for_status=lambda: None
        )
    )

    with caplog.at_level('WARNING'):
        got = pipeline.fetch_articles_from_api('2026-08-08')

    assert [a['url'] for a in got] == ['u1']
    assert '2026-08-07' in caplog.text


def test_review_page_images_actually_load_from_file_url(tmp_path):
    pytest.importorskip('playwright', reason='需要 playwright 打开 file:// 页面')
    from playwright.sync_api import sync_playwright

    result = run(articles(2), tmp_path)
    page_path = pipeline.render_review_page(
        result, tmp_path / '2026-08-10' / 'review.html'
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(page_path.as_uri())
            page.wait_for_load_state('networkidle')
            broken = page.evaluate("""() => {
              const imgs = Array.from(document.querySelectorAll('img'));
              return {
                total: imgs.length,
                broken: imgs.filter(i => !i.complete || i.naturalWidth === 0)
                            .map(i => i.getAttribute('src')),
              };
            }""")
        finally:
            browser.close()

    assert broken['total'] == 6
    assert broken['broken'] == []
