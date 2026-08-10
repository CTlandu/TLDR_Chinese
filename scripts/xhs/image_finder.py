import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

# 主项目的 image_extractor 用的是一串简单 UA，Bloomberg、NYT 这类站点直接回 403。
# 补一套完整的浏览器请求头，能多救回一部分配图。
BROWSER_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
}

TIMEOUT = 20


def find_og_image(url: str, timeout: int = TIMEOUT) -> Optional[str]:
    """从文章页拿 og:image / twitter:image。拿不到返回 None，不抛异常。"""
    if not url:
        return None
    try:
        response = requests.get(
            url, headers=BROWSER_HEADERS, timeout=timeout, allow_redirects=True
        )
        if response.status_code != 200:
            logging.info(f"补抓配图失败（HTTP {response.status_code}）：{url[:80]}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        for prop in ('og:image', 'twitter:image'):
            tag = soup.find('meta', property=prop) or soup.find('meta', attrs={'name': prop})
            if tag and tag.get('content'):
                return tag['content']

        return None

    except Exception as e:
        logging.info(f"补抓配图失败（{type(e).__name__}）：{url[:80]}")
        return None


def backfill_image(article: dict) -> Optional[str]:
    """文章没有 image_url 时去原文页补抓一次。"""
    existing = article.get('image_url')
    if existing:
        return existing

    found = find_og_image(article.get('url'))
    if found:
        logging.info(f"补抓到配图：{article.get('title', '')[:30]}")
    return found
