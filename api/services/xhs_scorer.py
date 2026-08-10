import json
import logging
import re
from typing import Dict, List, Optional

from openai import OpenAI

# 打分维度权重。调整这里即可改变选题倾向，无需改 prompt。
DIMENSION_WEIGHTS = {
    'recognition': 0.30,  # 中文读者对新闻主体的认知度
    'conflict': 0.25,     # 冲突性、反差感
    'numbers': 0.20,      # 数字冲击力
    'relevance': 0.25,    # 与普通人生活的相关度
}

FALLBACK_COUNT = 3
CONTENT_EXCERPT_LIMIT = 200

_FENCE_PATTERN = re.compile(r'^\s*```(?:json)?\s*(.*?)\s*```\s*$', re.DOTALL)


def strip_code_fence(text: str) -> str:
    """DeepSeek 有时会把 JSON 包在 markdown 代码块里，先剥壳。"""
    if not text:
        return ''
    match = _FENCE_PATTERN.match(text)
    return match.group(1) if match else text.strip()


def weighted_score(dimensions: Dict) -> float:
    """按 DIMENSION_WEIGHTS 加权求和。缺失或非数值的维度按 0 计。"""
    total = 0.0
    for key, weight in DIMENSION_WEIGHTS.items():
        value = dimensions.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        total += float(value) * weight
    return round(total, 4)


def parse_score_response(raw: str, articles: List[Dict]) -> List[Dict]:
    """把模型返回解析成按分数降序的 [{url, score, reason}]。

    模型漏掉的文章按 0 分补齐，保证返回条数与输入一致；
    模型编造的 url 直接丢弃。无法解析时抛 ValueError 交给调用方兜底。
    """
    payload = json.loads(strip_code_fence(raw))
    if not isinstance(payload, list):
        raise ValueError(f'期望 JSON 数组，实际是 {type(payload).__name__}')

    known_urls = {article.get('url') for article in articles if article.get('url')}
    scored: Dict[str, Dict] = {}

    for item in payload:
        if not isinstance(item, dict):
            continue
        url = item.get('url')
        if url not in known_urls or url in scored:
            continue
        scored[url] = {
            'url': url,
            'score': weighted_score(item),
            'reason': item.get('reason', ''),
        }

    for article in articles:
        url = article.get('url')
        if url and url not in scored:
            scored[url] = {'url': url, 'score': 0.0, 'reason': '模型未返回评分'}

    return sorted(scored.values(), key=lambda item: item['score'], reverse=True)


def _fallback(articles: List[Dict]) -> List[Dict]:
    return [
        {'url': article['url'], 'score': 0.0, 'reason': '打分失败，按原始顺序兜底'}
        for article in articles[:FALLBACK_COUNT]
        if article.get('url')
    ]


class XhsScorerService:
    def __init__(self, api_key: str, client=None):
        self.client = client or OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def _build_prompt(self, articles: List[Dict]) -> str:
        entries = []
        for article in articles:
            content = (article.get('content') or '')[:CONTENT_EXCERPT_LIMIT]
            entries.append(
                f"- url: {article.get('url')}\n"
                f"  标题: {article.get('title')}\n"
                f"  摘要: {content}"
            )
        articles_text = "\n".join(entries)

        return f"""
        你是一个小红书科技内容编辑，要从今天的科技新闻里挑出最可能在小红书上被转发和收藏的几条。

        今日新闻：
        {articles_text}

        请对每一条新闻按以下四个维度各打 0-10 分：

        - recognition（认知度）：中文读者对这条新闻的主体（公司、产品、人物）有多熟悉。
          苹果、马斯克、ChatGPT 这类是 8-10；只有从业者知道的 B 端公司是 0-3。
        - conflict（冲突性）：有没有反差、打脸、争议、意料之外的转折。
          纯粹的产品更新、融资公告是 0-3；某公司否认后被实锤是 8-10。
        - numbers（数字冲击力）：有没有让人一眼记住的数字。
          没有数字是 0；有但很平常是 3-5；量级夸张或对比强烈是 8-10。
        - relevance（相关度）：跟普通人的日常生活、工作、钱包有多大关系。
          底层芯片制程、企业级中间件是 0-3；直接影响手机、就业、学习方式的是 8-10。

        额外要求：
        - 与中国读者无关或在中国无法访问的产品（例如仅限美国本土的服务），recognition 和 relevance 都要相应压低。
        - reason 用一句中文说明为什么给这个分，不要复述新闻内容。

        只返回一个 JSON 数组，不要任何解释或 markdown 代码块，格式：
        [{{"url": "...", "recognition": 0, "conflict": 0, "numbers": 0, "relevance": 0, "reason": "..."}}]
        """

    def score_articles(self, articles: List[Dict]) -> List[Dict]:
        """对当天文章打分，返回按传播潜力降序的 [{url, score, reason}]。"""
        if not articles:
            return []

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个熟悉小红书内容生态的科技编辑，只输出 JSON。"},
                    {"role": "user", "content": self._build_prompt(articles)}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            raw = response.choices[0].message.content
            ranked = parse_score_response(raw, articles)
            logging.info(f"打分完成，共 {len(ranked)} 条，最高分 {ranked[0]['score'] if ranked else 0}")
            return ranked

        except Exception as e:
            logging.error(f"XHS scoring error: {str(e)}")
            return _fallback(articles)
