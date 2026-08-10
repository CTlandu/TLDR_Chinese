import json
import logging
import re
from typing import Dict, List, Optional

from openai import OpenAI

# 小红书硬限制是标题 20 / 正文 1000。目标值留出余量，避免贴着上限过审。
TITLE_LIMIT = 20
TITLE_TARGET = 18
BODY_LIMIT = 1000
BODY_TARGET = 950

# 真实的小红书科技号普遍挂 8-10 个标签，给 3-4 个反而不像原生内容
TAG_MIN = 6
TAG_MAX = 10

# 封面 1 张 + 正文卡 CARD_MIN~CARD_MAX 张 = 每篇 3-4 张图
CARD_MIN = 2
CARD_MAX = 3

CONTENT_EXCERPT_LIMIT = 1200

_FENCE_PATTERN = re.compile(r'^\s*```(?:json)?\s*(.*?)\s*```\s*$', re.DOTALL)


def strip_code_fence(text: str) -> str:
    if not text:
        return ''
    match = _FENCE_PATTERN.match(text)
    return match.group(1) if match else text.strip()


def parse_note_response(raw: str) -> Dict:
    payload = json.loads(strip_code_fence(raw))
    if not isinstance(payload, dict):
        raise ValueError(f'期望 JSON 对象，实际是 {type(payload).__name__}')

    return {
        'title': (payload.get('title') or '').strip(),
        'cover_hook': (payload.get('cover_hook') or '').strip(),
        'body': (payload.get('body') or '').strip(),
        'cards': [str(c).strip() for c in (payload.get('cards') or []) if str(c).strip()],
        'tags': [str(t).strip() for t in (payload.get('tags') or []) if str(t).strip()],
    }


def normalize_tags(tags: List[str]) -> List[str]:
    """去掉井号、去重、截到上限。少于下限只告警不阻断。"""
    seen = []
    for tag in tags:
        cleaned = tag.lstrip('#').strip()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)

    if len(seen) < TAG_MIN:
        logging.warning(f"标签只有 {len(seen)} 个，少于建议的 {TAG_MIN} 个")

    return seen[:TAG_MAX]


def split_into_cards(body: str, count: int = CARD_MIN) -> List[str]:
    """模型没给够正文卡时，按段落把正文切成 count 段兜底。"""
    paragraphs = [p.strip() for p in re.split(r'\n{2,}|\n', body) if p.strip()]
    if not paragraphs:
        return [body] * count if body else []
    if len(paragraphs) >= count:
        size = len(paragraphs) // count
        chunks = [
            '\n'.join(paragraphs[i * size:(i + 1) * size])
            for i in range(count - 1)
        ]
        chunks.append('\n'.join(paragraphs[(count - 1) * size:]))
        return chunks

    size = max(1, len(body) // count)
    return [body[i * size:(i + 1) * size] for i in range(count - 1)] + [body[(count - 1) * size:]]


def normalize_cards(cards: List[str], body: str) -> List[str]:
    if len(cards) > CARD_MAX:
        return cards[:CARD_MAX]
    if len(cards) < CARD_MIN:
        logging.warning(f"正文卡只有 {len(cards)} 张，按正文重新切分")
        return split_into_cards(body, CARD_MIN)
    return cards


def over_limit(note: Dict) -> Optional[str]:
    """返回超限说明，没超返回 None。字数按字符计，中文和英文字母各算 1。"""
    problems = []
    if len(note['title']) > TITLE_TARGET:
        problems.append(f"标题当前 {len(note['title'])} 字符，需压到 {TITLE_TARGET} 以内")
    if len(note['body']) > BODY_TARGET:
        problems.append(f"正文当前 {len(note['body'])} 字符，需压到 {BODY_TARGET} 以内")
    return '；'.join(problems) if problems else None


def hard_truncate(note: Dict) -> Dict:
    if len(note['title']) > TITLE_TARGET:
        logging.warning(f"标题重写后仍超限（{len(note['title'])}），硬截断到 {TITLE_TARGET}")
        note['title'] = note['title'][:TITLE_TARGET]
    if len(note['body']) > BODY_TARGET:
        logging.warning(f"正文重写后仍超限（{len(note['body'])}），硬截断到 {BODY_TARGET}")
        note['body'] = note['body'][:BODY_TARGET]
    return note


class XhsCopywriterService:
    def __init__(self, api_key: str, client=None):
        self.client = client or OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def _build_prompt(self, article: Dict) -> str:
        content = (article.get('content') or '')[:CONTENT_EXCERPT_LIMIT]
        return f"""
        把下面这条科技新闻改写成一篇小红书图文笔记。

        标题：{article.get('title')}
        内容：{content}

        写作要求：

        - 正文必须自身完整。读者不点开原文，也要能拿到"发生了什么、为什么重要、跟我有什么关系"这三件事。
        - 不要出现"详情见原文""点击链接""评论区领"这类引导跳转的表述。
        - cover_hook 是封面大字，写这条新闻最反差、最有冲突的那个点，不要把标题直译过去。
          它要能让人停下来，10-16 个字符。
        - title 是笔记标题，{TITLE_TARGET} 字符以内，口语、有具体信息，不要用"震惊""速看"这种标题党词。
        - body 是完整正文，{BODY_TARGET} 字符以内，短句，分 2-3 段。
        - cards 是把 body 拆成 {CARD_MIN}-{CARD_MAX} 段用于做图，每段 60-120 字符，
          拆分点要在语义边界上，不要从句子中间断开。cards 拼起来的信息量要等于 body。
        - tags 给 {TAG_MIN}-{TAG_MAX} 个，不带井号，用小红书上真实存在的话题词。

        只返回一个 JSON 对象，不要任何解释或 markdown 代码块，格式：
        {{"title": "...", "cover_hook": "...", "body": "...", "cards": ["...", "..."], "tags": ["...", "..."]}}
        """

    def _request(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个小红书科技博主，写口语化但有信息密度的笔记，只输出 JSON。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _enforce_limits(self, note: Dict, article: Dict) -> Dict:
        problem = over_limit(note)
        if not problem:
            return note

        logging.info(f"文案超限，请求重写：{problem}")
        rewrite_prompt = (
            f"{self._build_prompt(article)}\n\n"
            f"上一版不合格：{problem}。请在保住核心信息的前提下压缩，其余要求不变。"
        )
        try:
            note = parse_note_response(self._request(rewrite_prompt))
        except Exception as e:
            logging.warning(f"重写请求失败，沿用上一版并硬截断：{str(e)}")

        return hard_truncate(note)

    def generate_note(self, article: Dict) -> Optional[Dict]:
        """为单条新闻生成小红书笔记。失败返回 None，由调用方跳过这条候选。"""
        try:
            note = parse_note_response(self._request(self._build_prompt(article)))
            note = self._enforce_limits(note, article)
            note['tags'] = normalize_tags(note['tags'])
            note['cards'] = normalize_cards(note['cards'], note['body'])

            if not note['title'] or not note['body']:
                raise ValueError('标题或正文为空')
            if not note['cover_hook']:
                note['cover_hook'] = note['title']

            return note

        except Exception as e:
            logging.error(f"XHS copywriting error for {article.get('url')}: {str(e)}")
            return None
