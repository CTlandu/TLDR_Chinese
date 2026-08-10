from types import SimpleNamespace

from conftest import load_module

dedup = load_module('api/services/xhs_dedup.py')


def _articles(n, prefix='https://a.example/'):
    return [{'url': f'{prefix}{i}', 'title': f'第 {i} 条'} for i in range(n)]


def _post(url, status='drafted'):
    return SimpleNamespace(source_url=url, status=status)


def test_filters_out_already_drafted_urls():
    articles = _articles(10)
    seen = {'https://a.example/0', 'https://a.example/4', 'https://a.example/9'}

    remaining = dedup.filter_unpublished(articles, seen)

    assert len(remaining) == 7
    assert all(article['url'] not in seen for article in remaining)


def test_discarded_posts_still_count_as_seen():
    posts = [
        _post('https://a.example/0', status='discarded'),
        _post('https://a.example/1', status='published'),
        _post('https://a.example/2', status='drafted'),
    ]

    seen = dedup.collect_seen_urls(posts)

    assert seen == {
        'https://a.example/0',
        'https://a.example/1',
        'https://a.example/2',
    }


def test_empty_seen_set_returns_everything():
    articles = _articles(5)

    assert dedup.filter_unpublished(articles, set()) == articles


def test_duplicate_urls_within_input_are_collapsed():
    articles = _articles(3) + [{'url': 'https://a.example/1', 'title': '重复条目'}]

    remaining = dedup.filter_unpublished(articles, set())
    urls = [article['url'] for article in remaining]

    assert len(urls) == len(set(urls))
    assert len(remaining) == 3
    assert remaining[1]['title'] == '第 1 条'


def test_articles_without_url_are_dropped():
    articles = [{'title': '没有 url'}, {'url': '', 'title': '空 url'}] + _articles(2)

    remaining = dedup.filter_unpublished(articles, set())

    assert len(remaining) == 2


def test_collect_seen_urls_ignores_posts_without_source_url():
    posts = [_post('https://a.example/0'), SimpleNamespace(status='drafted')]

    assert dedup.collect_seen_urls(posts) == {'https://a.example/0'}


def test_order_is_preserved():
    articles = _articles(6)
    seen = {'https://a.example/2'}

    remaining = dedup.filter_unpublished(articles, seen)

    assert [a['url'] for a in remaining] == [
        'https://a.example/0',
        'https://a.example/1',
        'https://a.example/3',
        'https://a.example/4',
        'https://a.example/5',
    ]
