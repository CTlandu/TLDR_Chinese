import html as html_lib
import logging
from pathlib import Path
from typing import Dict, List, Optional

import requests

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1440
DEVICE_SCALE = 2
# 冷缓存的 CDN 回 HEAD 可能要将近 10 秒（实测 storage.ghost.io 9.6s）。
# 每天最多 3 张封面，宁可多等也不要把能用的图误判掉。
IMAGE_TIMEOUT = 15

SITE = 'tldrnewsletter.cn'
OUTRO_LEAD = '每天一份北美科技简报\n中英对照，五分钟读完'
OUTRO_NOTE = '完全免费，不用注册'

USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0 Safari/537.36'
)

TEMPLATE_PATH = Path(__file__).parent / 'templates' / 'card.html'

_OVERFLOW_PROBE = """() => {
  const panel = document.querySelector('.panel');
  return panel.scrollHeight > panel.clientHeight + 1;
}"""

# HEAD 探测通过不代表浏览器真能把图渲染出来（证书、防盗链、网络抖动都会让它挂）。
# 挂了的话 .media 只剩兜底底色，封面上方会是一块灰，比没有图更难看。
_MEDIA_LOADED_PROBE = """() => new Promise(resolve => {
  const el = document.querySelector('.media');
  if (!el) return resolve(true);
  const raw = getComputedStyle(el).backgroundImage;
  const match = raw.match(/url\\((['"]?)(.*?)\\1\\)/);
  if (!match) return resolve(false);
  const probe = new Image();
  probe.onload = () => resolve(true);
  probe.onerror = () => resolve(false);
  probe.src = match[2];
})"""


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


def _wrap(body: str) -> str:
    return TEMPLATE_PATH.read_text(encoding='utf-8').replace('{{BODY}}', body)


def build_card_html(
    variant: str,
    text: str = '',
    image_url: Optional[str] = None,
    source: str = '',
) -> str:
    """三种版式：cover 封面钩子、body 正文、outro 引流。

    卡面上不放任何品牌水印——小红书对满屏水印的内容判定为营销号，
    引流集中放在最后一张 outro 卡上。
    """
    if variant == 'outro':
        return _wrap(
            '<div class="panel outro">'
            f'<div class="lead">{html_lib.escape(OUTRO_LEAD)}</div>'
            f'<div class="site">{html_lib.escape(SITE)}</div>'
            f'<div class="note">{html_lib.escape(OUTRO_NOTE)}</div>'
            '</div>'
        )

    media = ''
    if variant == 'cover' and image_url:
        # 内联 style 属性本身用双引号包着，url("...") 里的双引号会把属性提前截断，
        # CSS 最后拿到的是空地址。转义之后 HTML 解析器会还原成正确的双引号。
        style = html_lib.escape(f'background-image: {_css_url(image_url)}', quote=True)
        media = f'<div class="media" style="{style}"></div>'

    rule = '<div class="rule"></div>' if variant == 'cover' else ''
    credit = f'<div class="source">{html_lib.escape(source)}</div>' if source else ''

    return _wrap(
        f'{media}'
        f'<div class="panel {variant}">'
        f'{rule}'
        f'<div class="text">{html_lib.escape(text)}</div>'
        f'{credit}'
        '</div>'
    )


def build_note_pages(
    note: Dict,
    image_url: Optional[str] = None,
    source: str = '',
) -> List[str]:
    """摊成待截图的 HTML 列表：1 张封面 + N 张正文 + 1 张引流卡。

    出处标在封面和每张正文卡的左下角；引流卡不标，它不承载新闻内容。
    """
    pages = [
        build_card_html(
            'cover',
            note.get('cover_hook') or note.get('title', ''),
            image_url=image_url,
            source=source,
        )
    ]
    pages.extend(
        build_card_html('body', card, source=source)
        for card in note.get('cards') or []
    )
    pages.append(build_card_html('outro'))
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


def render_note(
    note: Dict,
    out_dir,
    image_url: Optional[str] = None,
    source: str = '',
) -> List[Path]:
    """渲染一篇笔记的全部卡片，返回生成的 PNG 路径。

    配图不可用时自动降级为纯排版版式，不会少出图、也不会抛异常。
    """
    from playwright.sync_api import sync_playwright

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    usable = is_usable_image(image_url)
    if image_url and not usable:
        logging.info('配图不可用，封面降级为纯排版')

    cover_text = note.get('cover_hook') or note.get('title', '')
    pages = build_note_pages(note, image_url if usable else None, source=source)
    paths: List[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = _new_page(browser)
        try:
            for index, html in enumerate(pages, start=1):
                _settle(page, html)

                if 'class="media"' in html and not page.evaluate(_MEDIA_LOADED_PROBE):
                    logging.info('配图在浏览器里没加载出来，封面改用纯排版')
                    _settle(page, build_card_html('cover', cover_text, source=source))

                if page.evaluate(_OVERFLOW_PROBE):
                    logging.warning(f"第 {index} 张卡片文字溢出，检查文案长度")

                path = out_dir / f'{index:02d}.png'
                page.screenshot(path=str(path))
                paths.append(path)
        finally:
            browser.close()

    logging.info(f"渲染完成 {len(paths)} 张图 → {out_dir}")
    return paths
