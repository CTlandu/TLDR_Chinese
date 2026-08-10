import logging
import re
from typing import Optional
from urllib.parse import urlparse

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


def source_label(url: str) -> str:
    """左下角标注用的来源。完整 URL 在图上没人会手打，域名才是有用的信息。"""
    if not url:
        return ''
    host = urlparse(url).netloc
    return host[4:] if host.startswith('www.') else host


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
            logging.info(f"原文抓取失败（HTTP {response.status_code}）：{source_label(url)}")
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
            logging.info(f"原文正文过短（{len(text)} 字符），当作没抓到：{source_label(url)}")
            return None

        return text[:MAX_CHARS]

    except Exception as e:
        logging.info(f"原文抓取失败（{type(e).__name__}）：{source_label(url)}")
        return None
