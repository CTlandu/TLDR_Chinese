import logging
from typing import Dict, Iterable, List, Set


def collect_seen_urls(posts: Iterable) -> Set[str]:
    """收集所有已出稿的 source_url。

    刻意不按状态过滤：drafted 也算已出稿，否则昨天生成过但没选中的新闻
    今天会重新冒出来，审核页每天都是同一批。
    """
    return {
        post.source_url
        for post in posts
        if getattr(post, 'source_url', None)
    }


def filter_unpublished(articles: List[Dict], seen_urls: Set[str]) -> List[Dict]:
    """剔除已出稿的文章，并对输入内部的重复 url 去重（保留先出现的那条）。"""
    remaining = []
    taken = set()

    for article in articles:
        url = article.get('url')
        if not url or url in seen_urls or url in taken:
            continue
        taken.add(url)
        remaining.append(article)

    skipped = len(articles) - len(remaining)
    if skipped:
        logging.info(f"去重跳过 {skipped} 条（已出稿或重复）")

    return remaining


def seen_source_urls() -> Set[str]:
    """查询数据库中已出稿的 url 集合。"""
    from api.models.xhs_post import XhsPost
    return collect_seen_urls(XhsPost.objects())
