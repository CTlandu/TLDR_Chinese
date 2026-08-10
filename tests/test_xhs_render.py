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


def test_card_html_escapes_user_text():
    html = render.build_card_html('body', '<script>alert(1)</script> & 收工')

    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html
    assert '&amp;' in html


def test_cover_variant_embeds_image_and_body_variant_does_not():
    cover = render.build_card_html('cover', '钩子', image_url='https://img.example/a.jpg')
    body = render.build_card_html('body', '正文')

    assert 'url("https://img.example/a.jpg")' in cover
    assert render.SCRIM_WITH_IMAGE in cover
    assert 'background-image: none' in body
    assert render.SCRIM_PLAIN in body


def test_no_unreplaced_placeholders_remain():
    for html in render.build_note_pages(NOTE, 'https://img.example/a.jpg'):
        assert '{{' not in html


def test_note_pages_are_cover_plus_each_card():
    pages = render.build_note_pages(NOTE)

    assert len(pages) == len(NOTE['cards']) + 1
    assert '01 / 04' in pages[0]
    assert '04 / 04' in pages[-1]


def test_renders_one_file_per_page_at_full_resolution(tmp_path, monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head())

    paths = render.render_note(NOTE, tmp_path, image_url='https://img.example/a.jpg')

    assert len(paths) == 4
    for path in paths:
        assert path.exists()
        assert png_size(path) == (
            render.IMAGE_WIDTH * render.DEVICE_SCALE,
            render.IMAGE_HEIGHT * render.DEVICE_SCALE,
        )


def test_missing_image_still_produces_full_card_count(tmp_path):
    paths = render.render_note(NOTE, tmp_path, image_url=None)

    assert len(paths) == 4
    assert all(path.exists() for path in paths)


def test_broken_image_degrades_without_raising(tmp_path, monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head(status=404))

    paths = render.render_note(NOTE, tmp_path, image_url='https://img.example/gone.jpg')

    assert len(paths) == 4


def test_rerun_overwrites_instead_of_failing(tmp_path, monkeypatch):
    monkeypatch.setattr(render.requests, 'head', lambda url, **kw: _head())

    first = render.render_note(NOTE, tmp_path)
    stamp = first[0].stat().st_mtime_ns
    second = render.render_note(NOTE, tmp_path)

    assert [p.name for p in first] == [p.name for p in second]
    assert second[0].stat().st_mtime_ns >= stamp
    assert len(list(tmp_path.glob('*.png'))) == 4


def test_cover_at_title_length_limit_does_not_overflow():
    hook = '一二三四五六七八九十一二三四五六七八'      # 18 字符，标题上限
    assert len(hook) == 18

    html = render.build_card_html('cover', hook)

    assert render.html_overflows(html) is False


def test_overflow_probe_actually_detects_overflow():
    html = render.build_card_html('body', '很长的一段文字。' * 200)

    assert render.html_overflows(html) is True
