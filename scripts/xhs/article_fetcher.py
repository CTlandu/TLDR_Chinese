import logging
import re
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from image_finder import BROWSER_HEADERS

TIMEOUT = 25
MAX_CHARS = 6000
MIN_USEFUL_CHARS = 400

# 正文之外的噪音，抓下来只会污染写作素材
_DROP_TAGS = ('script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'noscript')

# 按优先级找正文容器，找不到再退回全文
_ARTICLE_SELECTORS = (
    'article',
    '[itemprop="articleBody"]',
    '.article-body',
    '.post-content',
    '.entry-content',
    'main',
)


# 纯跟踪参数，删掉不影响访问
_TRACKING_PARAMS = ('utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
                    'utm_content', 'smid', 'ref', 'source')


def clean_url(url: str) -> str:
    """去掉跟踪参数，保留其余查询串。

    Bloomberg 的 accessToken、NYT 的 unlocked_article_code 是免付费墙的钥匙，
    删了读者就只能看到订阅墙，所以只清跟踪参数，不做整段截断。
    """
    if not url:
        return ''
    parts = urlparse(url)
    kept = [
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k not in _TRACKING_PARAMS
    ]
    return urlunparse(parts._replace(query=urlencode(kept)))


def display_url(url: str) -> str:
    """卡片上展示用的短形式：去掉协议、www 和整个查询串。

    图片上的链接点不了，它的作用是让人一眼看出出处可信。
    带 token 的完整链接有四百多字符，铺在卡片上是一片 base64，反效果。
    """
    if not url:
        return ''
    parts = urlparse(url)
    host = parts.netloc[4:] if parts.netloc.startswith('www.') else parts.netloc
    return f'{host}{parts.path}'.rstrip('/')


def _clean(text: str) -> str:
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def fetch_article_text(url: str, timeout: int = TIMEOUT) -> Optional[str]:
    """抓英文原文正文。抓不到返回 None，调用方回退到 TLDR 的中文摘要。"""
    if not url:
        return None
    try:
        response = requests.get(
            url, headers=BROWSER_HEADERS, timeout=timeout, allow_redirects=True
        )
        if response.status_code != 200:
            logging.info(f"原文抓取失败（HTTP {response.status_code}）：{display_url(url)}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(_DROP_TAGS):
            tag.decompose()

        container = None
        for selector in _ARTICLE_SELECTORS:
            container = soup.select_one(selector)
            if container:
                break

        text = _clean((container or soup).get_text('\n'))

        if len(text) < MIN_USEFUL_CHARS:
            logging.info(f"原文正文过短（{len(text)} 字符），当作没抓到：{display_url(url)}")
            return None

        return text[:MAX_CHARS]

    except Exception as e:
        logging.info(f"原文抓取失败（{type(e).__name__}）：{display_url(url)}")
        return None
