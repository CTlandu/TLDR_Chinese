import json

import pytest
from conftest import FakeDeepSeekClient, load_module

scorer = load_module('api/services/xhs_scorer.py')


ARTICLES = [
    {'url': 'https://a.example/1', 'title': '苹果发布新芯片', 'content': '内容 A'},
    {'url': 'https://a.example/2', 'title': '某 B 端公司完成融资', 'content': '内容 B'},
    {'url': 'https://a.example/3', 'title': '模型跑分刷新纪录', 'content': '内容 C'},
    {'url': 'https://a.example/4', 'title': '数据中心扩容', 'content': '内容 D'},
]


def _dims(url, recognition=0, conflict=0, numbers=0, relevance=0, reason='r'):
    return {
        'url': url,
        'recognition': recognition,
        'conflict': conflict,
        'numbers': numbers,
        'relevance': relevance,
        'reason': reason,
    }


def _service(client):
    return scorer.XhsScorerService(api_key='unused', client=client)


def test_normal_response_sorted_desc_and_count_matches_input():
    payload = [
        _dims(ARTICLES[0]['url'], recognition=9, relevance=8),
        _dims(ARTICLES[1]['url'], recognition=1),
        _dims(ARTICLES[2]['url'], recognition=5, numbers=9),
        _dims(ARTICLES[3]['url'], recognition=2),
    ]
    client = FakeDeepSeekClient(content=json.dumps(payload))

    ranked = _service(client).score_articles(ARTICLES)

    assert len(ranked) == len(ARTICLES)
    assert [item['score'] for item in ranked] == sorted(
        (item['score'] for item in ranked), reverse=True
    )
    assert ranked[0]['url'] == ARTICLES[0]['url']
    assert ranked[0]['reason'] == 'r'


def test_response_wrapped_in_markdown_fence_is_parsed():
    payload = [_dims(ARTICLES[0]['url'], recognition=10)]
    client = FakeDeepSeekClient(content=f"```json\n{json.dumps(payload)}\n```")

    ranked = _service(client).score_articles(ARTICLES)

    assert ranked[0]['url'] == ARTICLES[0]['url']
    assert ranked[0]['score'] == pytest.approx(3.0)


def test_invalid_json_falls_back_to_first_three_without_raising():
    client = FakeDeepSeekClient(content='这是模型的一段闲聊，不是 JSON')

    ranked = _service(client).score_articles(ARTICLES)

    assert [item['url'] for item in ranked] == [a['url'] for a in ARTICLES[:3]]
    assert all(item['score'] == 0.0 for item in ranked)


def test_non_array_json_falls_back():
    client = FakeDeepSeekClient(content='{"url": "https://a.example/1"}')

    ranked = _service(client).score_articles(ARTICLES)

    assert len(ranked) == 3


def test_hallucinated_url_is_dropped_and_rest_survive():
    payload = [
        _dims('https://not-in-input.example/9', recognition=10),
        _dims(ARTICLES[0]['url'], recognition=6),
    ]
    client = FakeDeepSeekClient(content=json.dumps(payload))

    ranked = _service(client).score_articles(ARTICLES)
    urls = [item['url'] for item in ranked]

    assert 'https://not-in-input.example/9' not in urls
    assert len(ranked) == len(ARTICLES)
    assert ranked[0]['url'] == ARTICLES[0]['url']


def test_articles_omitted_by_model_are_backfilled_at_zero():
    payload = [_dims(ARTICLES[2]['url'], recognition=7)]
    client = FakeDeepSeekClient(content=json.dumps(payload))

    ranked = _service(client).score_articles(ARTICLES)
    by_url = {item['url']: item for item in ranked}

    assert len(ranked) == len(ARTICLES)
    assert by_url[ARTICLES[0]['url']]['score'] == 0.0
    assert by_url[ARTICLES[0]['url']]['reason'] == '模型未返回评分'
    assert by_url[ARTICLES[2]['url']]['score'] > 0


def test_empty_input_returns_empty_without_calling_api():
    client = FakeDeepSeekClient(content='[]')

    ranked = _service(client).score_articles([])

    assert ranked == []
    assert client.calls == []


def test_api_exception_falls_back():
    client = FakeDeepSeekClient(error=RuntimeError('connection reset'))

    ranked = _service(client).score_articles(ARTICLES)

    assert len(ranked) == 3
    assert ranked[0]['reason'] == '打分失败，按原始顺序兜底'


def test_weight_change_reorders_same_model_output(monkeypatch):
    payload = [
        _dims(ARTICLES[0]['url'], recognition=10),
        _dims(ARTICLES[1]['url'], numbers=10),
    ]
    raw = json.dumps(payload)

    default_ranked = scorer.parse_score_response(raw, ARTICLES)
    assert default_ranked[0]['url'] == ARTICLES[0]['url']

    monkeypatch.setattr(
        scorer,
        'DIMENSION_WEIGHTS',
        {'recognition': 0.1, 'conflict': 0.0, 'numbers': 0.8, 'relevance': 0.1},
    )
    reweighted = scorer.parse_score_response(raw, ARTICLES)

    assert reweighted[0]['url'] == ARTICLES[1]['url']


def test_non_numeric_dimension_is_ignored_not_crashing():
    payload = [_dims(ARTICLES[0]['url'], recognition='高')]
    payload[0]['conflict'] = None
    payload[0]['numbers'] = True
    client = FakeDeepSeekClient(content=json.dumps(payload))

    ranked = _service(client).score_articles(ARTICLES)

    assert len(ranked) == len(ARTICLES)
    assert all(isinstance(item['score'], float) for item in ranked)
