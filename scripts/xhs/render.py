import html as html_lib
import logging
from pathlib import Path
from typing import Dict, List, Optional

import requests

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1440
DEVICE_SCALE = 2
IMAGE_TIMEOUT = 8

FOOTER_TEXT = 'tldrnewsletter.cn'
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0 Safari/537.36'
)

TEMPLATE_PATH = Path(__file__).parent / 'templates' / 'card.html'

COVER_STYLE = {
    'STAGE_ALIGN': 'flex-end',
    'FONT_SIZE': '84px',
    'LINE_HEIGHT': '1.28',
    'FONT_WEIGHT': '700',
    'TRACKING': '-0.02em',
    'RULE': '<div class="rule"></div>',
}

BODY_STYLE = {
    'STAGE_ALIGN': 'center',
    'FONT_SIZE': '52px',
    'LINE_HEIGHT': '1.72',
    'FONT_WEIGHT': '400',
    'TRACKING': '0',
    'RULE': '',
}

# 有配图时压一层从下往上的深色渐变，保证白字始终压得住背景
SCRIM_WITH_IMAGE = (
    'linear-gradient(180deg, rgba(18,16,15,0.70) 0%, '
    'rgba(18,16,15,0.58) 38%, rgba(18,16,15,0.96) 100%)'
)
SCRIM_PLAIN = (
    'radial-gradient(120% 80% at 15% 0%, rgba(232,80,58,0.16) 0%, '
    'rgba(18,16,15,0) 60%)'
)

_OVERFLOW_PROBE = """() => {
  const stage = document.querySelector('.stage');
  return stage.scrollHeight > stage.clientHeight + 1;
}"""


def is_usable_image(url: Optional[str], timeout: int = IMAGE_TIMEOUT) -> bool:
    """确认配图真的能用：可达、状态 200、content-type 是图片。

    只发 HEAD，不下整张图——判断可用性不需要图本身。
    """
    if not url:
        return False
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)

        # 有些 CDN 直接拒绝 HEAD。这时候用 GET 探一下头再断开，
        # 否则会把本来能用的图误判成不可用。
        if response.status_code in (403, 405, 501):
            response = requests.get(
                url, headers=headers, timeout=timeout,
                allow_redirects=True, stream=True
            )
            response.close()

        if response.status_code != 200:
            logging.info(f"配图不可用（HTTP {response.status_code}）：{url}")
            return False

        content_type = response.headers.get('Content-Type', '')
        if not content_type.lower().startswith('image/'):
            logging.info(f"配图不是图片（Content-Type: {content_type}）：{url}")
            return False

        return True

    except Exception as e:
        logging.info(f"配图探测失败（{type(e).__name__}）：{url}")
        return False


def _css_url(url: str) -> str:
    safe = url.replace('\\', '\\\\').replace('"', '\\"')
    return f'url("{safe}")'


def build_card_html(
    variant: str,
    text: str,
    counter: str = '',
    image_url: Optional[str] = None,
) -> str:
    template = TEMPLATE_PATH.read_text(encoding='utf-8')
    style = COVER_STYLE if variant == 'cover' else BODY_STYLE

    values = dict(style)
    values['TEXT'] = html_lib.escape(text)
    values['FOOTER'] = FOOTER_TEXT
    values['COUNTER'] = counter
    values['BACKDROP_IMAGE'] = _css_url(image_url) if image_url else 'none'
    values['SCRIM'] = SCRIM_WITH_IMAGE if image_url else SCRIM_PLAIN

    for key, value in values.items():
        template = template.replace('{{' + key + '}}', value)

    return template


def build_note_pages(note: Dict, image_url: Optional[str] = None) -> List[str]:
    """把一篇笔记摊成待截图的 HTML 列表：1 张封面 + N 张正文卡。"""
    cards = note.get('cards') or []
    total = len(cards) + 1

    pages = [
        build_card_html(
            'cover',
            note.get('cover_hook') or note.get('title', ''),
            counter=f'01 / {total:02d}',
            image_url=image_url,
        )
    ]
    for index, card in enumerate(cards, start=2):
        pages.append(
            build_card_html('body', card, counter=f'{index:02d} / {total:02d}')
        )

    return pages


def _new_page(browser):
    return browser.new_page(
        viewport={'width': IMAGE_WIDTH, 'height': IMAGE_HEIGHT},
        device_scale_factor=DEVICE_SCALE,
    )


def _settle(page, html: str):
    page.set_content(html, wait_until='networkidle')
    page.evaluate('() => document.fonts.ready')


def html_overflows(html: str) -> bool:
    """文字有没有溢出可视区。用于校验字号与文案长度的配合。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = _new_page(browser)
        try:
            _settle(page, html)
            return bool(page.evaluate(_OVERFLOW_PROBE))
        finally:
            browser.close()


def render_note(note: Dict, out_dir, image_url: Optional[str] = None) -> List[Path]:
    """渲染一篇笔记的全部卡片，返回生成的 PNG 路径。

    配图不可用时自动降级为纯排版版式，不会少出图、也不会抛异常。
    """
    from playwright.sync_api import sync_playwright

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    usable = is_usable_image(image_url)
    if image_url and not usable:
        logging.info('配图不可用，封面降级为纯排版')

    pages = build_note_pages(note, image_url if usable else None)
    paths: List[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = _new_page(browser)
        try:
            for index, html in enumerate(pages, start=1):
                _settle(page, html)
                if page.evaluate(_OVERFLOW_PROBE):
                    logging.warning(f"第 {index} 张卡片文字溢出，检查文案长度")

                path = out_dir / f'{index:02d}.png'
                page.screenshot(path=str(path))
                paths.append(path)
        finally:
            browser.close()

    logging.info(f"渲染完成 {len(paths)} 张图 → {out_dir}")
    return paths
