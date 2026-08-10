import struct
from types import SimpleNamespace

import pytest
import requests
from conftest import load_module

render = load_module('scripts/xhs/render.py')

playwright = pytest.importorskip('playwright', reason='渲染测试需要 playwright')


NOTE = {
    'title': '苹果这次真的换芯了',
    'cover_hook': '苹果悄悄换掉了它',
    'cards': ['第一张正文卡的内容。', '第二张正文卡的内容。', '第三张正文卡的内容。'],
}


def png_size(path):
    with open(path, 'rb') as f:
        header = f.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n', f'{path} 不是 PNG'
    return struct.unpack('>II', header[16:24])


def _head(status=200, content_type='image/jpeg'):
    return SimpleNamespace(
        status_code=status,
        headers={'Content-Type': content_type},
    )


def test_usable_image_accepts_200_image_response(monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head())

    assert render.is_usable_image('https://img.example/a.jpg') is True


def test_missing_url_is_not_usable_and_makes_no_request(monkeypatch):
    def explode(*a, **kw):
        raise AssertionError('不该发请求')

    monkeypatch.setattr(render.requests, 'head', explode)

    assert render.is_usable_image(None) is False
    assert render.is_usable_image('') is False


def test_404_image_is_not_usable(monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head(status=404))

    assert render.is_usable_image('https://img.example/missing.jpg') is False


def test_html_page_is_not_usable_as_image(monkeypatch):
    monkeypatch.setattr(
        render.requests, 'head',
        lambda url, **kw: _head(content_type='text/html; charset=utf-8')
    )

    assert render.is_usable_image('https://page.example/article') is False


def test_timeout_degrades_and_forwards_the_timeout_value(monkeypatch):
    seen = {}

    def fake_head(url, **kwargs):
        seen.update(kwargs)
        raise requests.exceptions.Timeout('too slow')

    monkeypatch.setattr(render.requests, 'head', fake_head)

    assert render.is_usable_image('https://slow.example/a.jpg', timeout=3) is False
    assert seen['timeout'] == 3


@pytest.mark.parametrize('status', [403, 405, 501])
def test_head_rejection_falls_back_to_get(monkeypatch, status):
    calls = []

    def fake_head(url, **kw):
        calls.append('head')
        return _head(status=status)

    def fake_get(url, **kw):
        calls.append('get')
        assert kw.get('stream') is True
        return SimpleNamespace(
            status_code=200,
            headers={'Content-Type': 'image/png'},
            close=lambda: calls.append('close'),
        )

    monkeypatch.setattr(render.requests, 'head', fake_head)
    monkeypatch.setattr(render.requests, 'get', fake_get)

    assert render.is_usable_image('https://cdn.example/a.png') is True
    assert calls == ['head', 'get', 'close']


def test_get_fallback_still_rejects_non_images(monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head(status=405))
    monkeypatch.setattr(
        render.requests, 'get',
        lambda url, **kw: SimpleNamespace(
            status_code=200,
            headers={'Content-Type': 'text/html'},
            close=lambda: None,
        )
    )

    assert render.is_usable_image('https://cdn.example/page') is False


def test_card_html_escapes_user_text():
    html = render.build_card_html('body', '<script>alert(1)</script> & 收工')

    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html
    assert '&amp;' in html


def test_cover_variant_embeds_image_and_body_variant_does_not():
    cover = render.build_card_html('cover', '钩子', image_url='https://img.example/a.jpg')
    body = render.build_card_html('body', '正文')

    assert 'url("https://img.example/a.jpg")' in cover
    assert 'class="media"' in cover
    assert 'class="media"' not in body


def test_cover_without_image_has_no_media_block():
    cover = render.build_card_html('cover', '钩子')

    assert 'class="media"' not in cover
    assert 'panel cover' in cover


def test_no_brand_watermark_anywhere_except_the_outro_card():
    """满屏水印会被判定成营销号，引流只集中在最后一张。"""
    for html in render.build_note_pages(NOTE, 'https://img.example/a.jpg')[:-1]:
        assert 'TLDR' not in html
        assert render.SITE not in html

    assert render.SITE in render.build_note_pages(NOTE)[-1]


def test_no_unreplaced_placeholders_remain():
    for html in render.build_note_pages(NOTE, 'https://img.example/a.jpg'):
        assert '{{' not in html


def test_note_pages_are_cover_plus_cards_plus_outro():
    pages = render.build_note_pages(NOTE)

    assert len(pages) == len(NOTE['cards']) + 2
    assert 'panel cover' in pages[0]
    assert 'panel body' in pages[1]
    assert 'panel outro' in pages[-1]


def test_outro_card_carries_the_site_and_free_note():
    outro = render.build_card_html('outro')

    assert render.SITE in outro
    assert render.OUTRO_NOTE in outro
    assert render.html_overflows(outro) is False


def test_renders_one_file_per_page_at_full_resolution(tmp_path, monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head())

    paths = render.render_note(NOTE, tmp_path, image_url='https://img.example/a.jpg')

    assert len(paths) == 5
    for path in paths:
        assert path.exists()
        assert png_size(path) == (
            render.IMAGE_WIDTH * render.DEVICE_SCALE,
            render.IMAGE_HEIGHT * render.DEVICE_SCALE,
        )


def test_missing_image_still_produces_full_card_count(tmp_path):
    paths = render.render_note(NOTE, tmp_path, image_url=None)

    assert len(paths) == 5
    assert all(path.exists() for path in paths)


def test_broken_image_degrades_without_raising(tmp_path, monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head(status=404))

    paths = render.render_note(NOTE, tmp_path, image_url='https://img.example/gone.jpg')

    assert len(paths) == 5


def test_unloadable_image_falls_back_to_plain_cover(tmp_path, monkeypatch):
    """HEAD 探测通过但浏览器加载不出来时，封面不能留一块兜底灰。"""
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head())

    paths = render.render_note(
        NOTE, tmp_path, image_url='https://does-not-resolve.invalid/a.jpg'
    )

    assert len(paths) == 5

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(paths[0].as_uri())
            # 兜底灰 #E7E2DA 不应该出现在成图左上角，米白底才对
            pixel = page.evaluate("""async () => {
              const img = document.querySelector('img');
              await img.decode();
              const c = document.createElement('canvas');
              c.width = img.naturalWidth; c.height = img.naturalHeight;
              c.getContext('2d').drawImage(img, 0, 0);
              const d = c.getContext('2d').getImageData(20, 20, 1, 1).data;
              return [d[0], d[1], d[2]];
            }""")
        finally:
            browser.close()

    assert pixel == [246, 243, 238]


def test_rerun_overwrites_instead_of_failing(tmp_path, monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head())

    first = render.render_note(NOTE, tmp_path)
    stamp = first[0].stat().st_mtime_ns
    second = render.render_note(NOTE, tmp_path)

    assert [p.name for p in first] == [p.name for p in second]
    assert second[0].stat().st_mtime_ns >= stamp
    assert len(list(tmp_path.glob('*.png'))) == 5


def test_cover_at_title_length_limit_does_not_overflow():
    hook = '一二三四五六七八九十一二三四五六七八'      # 18 字符，标题上限
    assert len(hook) == 18

    html = render.build_card_html('cover', hook)

    assert render.html_overflows(html) is False


def test_overflow_probe_actually_detects_overflow():
    html = render.build_card_html('body', '很长的一段文字。' * 200)

    assert render.html_overflows(html) is True
