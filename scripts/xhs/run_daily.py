import argparse
import html as html_lib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

TOP_N = 3
OUTPUT_ROOT = SCRIPT_DIR / 'output'
REVIEW_TEMPLATE = SCRIPT_DIR / 'templates' / 'review.html'

TITLE_LIMIT = 20
BODY_LIMIT = 1000

PUBLIC_API = 'https://www.tldrnewsletter.cn/api/newsletter/{date}'

INPUT_FILENAME = 'candidates_input.json'
NOTES_FILENAME = 'notes.json'

logger = logging.getLogger(__name__)


def source_label(url: str) -> str:
    from article_fetcher import source_label as _label
    return _label(url)


def flatten_sections(sections) -> List[Dict]:
    """把 DailyNewsletter.sections 摊平成文章列表。缺 articles 键的 section 直接跳过。"""
    articles = []
    for section in sections or []:
        if not isinstance(section, dict):
            continue
        for article in section.get('articles') or []:
            if not isinstance(article, dict):
                continue
            item = dict(article)
            item['section'] = section.get('section', '')
            articles.append(item)
    return articles


def select_candidates(articles: List[Dict], scorer, top_n: int = TOP_N) -> List[Dict]:
    """打分后取前 top_n，把排名信息挂回原文章。"""
    ranked = scorer.score_articles(articles)
    by_url = {a['url']: a for a in articles if a.get('url')}

    picked = []
    for entry in ranked:
        article = by_url.get(entry['url'])
        if article is None:
            continue
        picked.append({'article': article, 'score': entry['score'], 'reason': entry['reason']})
        if len(picked) == top_n:
            break

    return picked


def run_pipeline(
    articles: List[Dict],
    scorer,
    copywriter,
    render_fn,
    out_root,
    date_str: str,
    top_n: int = TOP_N,
) -> Dict:
    """生成当天的候选笔记。任何一条失败都不影响其余条目。"""
    result = {
        'date': date_str,
        'requested': top_n,
        'candidates': [],
        'failures': [],
        'notice': None,
    }

    if not articles:
        result['notice'] = f'{date_str} 没有可用的候选新闻（当天无刊，或当天新闻都已经出过稿）。'
        return result

    out_root = Path(out_root)

    for index, picked in enumerate(select_candidates(articles, scorer, top_n), start=1):
        article = picked['article']

        note = copywriter.generate_note(article)
        if note is None:
            logger.warning(f"第 {index} 条文案生成失败：{article.get('title')}")
            result['failures'].append({
                'index': index,
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'stage': '文案生成',
            })
            continue

        out_dir = out_root / date_str / f'{index:02d}'
        try:
            images = render_fn(
                note, out_dir, article.get('image_url'), source_label(article.get('url', ''))
            )
        except Exception as e:
            logger.error(f"第 {index} 条渲染失败：{str(e)}")
            result['failures'].append({
                'index': index,
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'stage': '出图',
            })
            continue

        result['candidates'].append({
            'index': index,
            'note': note,
            'images': [Path(p) for p in images],
            'out_dir': out_dir,
            'source_url': article.get('url', ''),
            'source_title': article.get('title', ''),
            'score': picked['score'],
            'reason': picked['reason'],
        })

    if not result['candidates'] and not result['notice']:
        result['notice'] = f'{date_str} 的候选全部生成失败，详见下方失败列表。'

    return result


def _count_span(text: str, limit: int) -> str:
    over = ' over' if len(text) > limit else ''
    return f'<span class="count{over}">{len(text)} / {limit}</span>'


def _field(label: str, value: str, field_id: str, extra: str = '') -> str:
    return (
        f'<div class="field">'
        f'<div class="label">{label}{extra}'
        f'<button data-copy="{field_id}">复制</button></div>'
        f'<div class="value" id="{field_id}">{html_lib.escape(value)}</div>'
        f'</div>'
    )


def _candidate_html(candidate: Dict) -> str:
    note = candidate['note']
    index = candidate['index']
    prefix = f'c{index}'

    shots = ''.join(
        f'<img src="{index:02d}/{image.name}" alt="第 {index} 篇第 {n} 张">'
        for n, image in enumerate(candidate['images'], start=1)
    )

    tags_text = ' '.join(f'#{tag}' for tag in note.get('tags', []))

    return f"""
  <section class="candidate">
    <div class="shots">{shots}</div>
    <div class="detail">
      <div class="index">第 <b>{index:02d}</b> 篇 · 打分 {candidate['score']}</div>
      {_field('标题', note.get('title', ''), f'{prefix}-title',
              _count_span(note.get('title', ''), TITLE_LIMIT))}
      {_field('正文', note.get('body', ''), f'{prefix}-body',
              _count_span(note.get('body', ''), BODY_LIMIT))}
      {_field('标签', tags_text, f'{prefix}-tags')}
      <p class="meta">选它的理由：{html_lib.escape(candidate['reason'] or '—')}</p>
      <p class="meta">原文：<a href="{html_lib.escape(candidate['source_url'])}">{html_lib.escape(candidate['source_title'])}</a></p>
    </div>
  </section>"""


def render_review_page(result: Dict, out_path) -> Path:
    """产出当天的审核页。无论有没有候选都会产出，避免让人误以为脚本挂了。"""
    template = REVIEW_TEMPLATE.read_text(encoding='utf-8')

    candidates = result['candidates']
    summary = f"今日候选 {len(candidates)} / {result['requested']} 篇"
    if result['failures']:
        summary += f"，{len(result['failures'])} 篇生成失败"

    notice = ''
    if result['notice']:
        notice = f'<div class="notice">{html_lib.escape(result["notice"])}</div>'

    failures = ''
    if result['failures']:
        rows = ''.join(
            f'<div>第 {f["index"]:02d} 篇在「{f["stage"]}」阶段失败：'
            f'{html_lib.escape(f["title"])}</div>'
            for f in result['failures']
        )
        failures = f'<div class="failures">{rows}</div>'

    html = (
        template
        .replace('{{DATE}}', html_lib.escape(result['date']))
        .replace('{{SUMMARY}}', summary)
        .replace('{{NOTICE}}', notice)
        .replace('{{CANDIDATES}}', ''.join(_candidate_html(c) for c in candidates))
        .replace('{{FAILURES}}', failures)
    )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')
    return out_path


def write_note_json(candidate: Dict) -> Path:
    """把文案原样落盘，方便发布时读取，也方便手动兜底。"""
    path = candidate['out_dir'] / 'note.json'
    payload = {
        'index': candidate['index'],
        'title': candidate['note'].get('title'),
        'body': candidate['note'].get('body'),
        'tags': candidate['note'].get('tags'),
        'images': [str(p.name) for p in candidate['images']],
        'source_url': candidate['source_url'],
        'source_title': candidate['source_title'],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return path


def today_eastern() -> str:
    import pytz
    return datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')


def fetch_articles_from_api(date_str: str) -> List[Dict]:
    """从生产站点的公开接口取当天新闻，不需要数据库凭据。"""
    response = requests.get(PUBLIC_API.format(date=date_str), timeout=30)
    response.raise_for_status()
    payload = response.json()

    returned = payload.get('currentDate')
    if returned != date_str:
        logger.warning(f"接口返回的是 {returned} 的内容，不是 {date_str}")

    return flatten_sections(payload.get('sections'))


def fetch_articles_from_db(date_str: str) -> List[Dict]:
    from api.models.article import DailyNewsletter
    newsletter = DailyNewsletter.objects(date=date_str).first()
    return flatten_sections(newsletter.sections) if newsletter else []


def seen_urls_from_output(root) -> set:
    """扫历史产物目录收集已出稿的 url。

    api 来源模式下没有数据库，产物目录本身就是去重依据。
    """
    seen = set()
    for note_path in Path(root).glob('*/*/note.json'):
        try:
            url = json.loads(note_path.read_text(encoding='utf-8')).get('source_url')
        except Exception:
            continue
        if url:
            seen.add(url)
    return seen


class PreparedScorer:
    """把外部已经排好的顺序原样喂给流水线，替代 DeepSeek 打分。"""

    def __init__(self, picks: List[Dict]):
        self.picks = picks

    def score_articles(self, articles):
        return [
            {
                'url': pick['url'],
                'score': float(pick.get('score', 0.0)),
                'reason': pick.get('reason', ''),
            }
            for pick in self.picks
        ]


class PreparedCopywriter:
    """把外部写好的文案原样喂给流水线，替代 DeepSeek 文案生成。"""

    def __init__(self, picks: List[Dict]):
        self.by_url = {p['url']: p['note'] for p in picks if p.get('note')}

    def generate_note(self, article):
        note = self.by_url.get(article.get('url'))
        return dict(note) if note else None


def normalize_note(note: Dict) -> Dict:
    """手写文案同样要过字数和标签的硬约束，不因为是人写的就免检。"""
    from api.services.xhs_copywriter import hard_truncate, normalize_cards, normalize_tags

    note = dict(note)
    note.setdefault('title', '')
    note.setdefault('body', '')
    note['tags'] = normalize_tags(note.get('tags') or [])
    note = hard_truncate(note)
    note['cards'] = normalize_cards(note.get('cards') or [], note['body'])
    if not note.get('cover_hook'):
        note['cover_hook'] = note['title']
    return note


def attach_source_text(articles: List[Dict], workers: int = 6) -> None:
    """给每篇挂上英文原文正文，供写文案时当素材。

    TLDR 里大量链接指向付费墙站点，抓不到是常态。抓不到就把 source_text 留空，
    写的人看到空值就知道这条只有 TLDR 的中文摘要可用。
    """
    from concurrent.futures import ThreadPoolExecutor

    from article_fetcher import fetch_article_text

    with ThreadPoolExecutor(max_workers=workers) as pool:
        texts = list(pool.map(lambda a: fetch_article_text(a.get('url')), articles))

    got = 0
    for article, text in zip(articles, texts):
        article['source_text'] = text or ''
        got += bool(text)

    logger.info(f"抓到英文原文 {got}/{len(articles)} 篇")


def cmd_prepare(date_str: str, source: str) -> Path:
    """第一段：取当天新闻、去重，把待选清单落盘等人（或模型）来排。"""
    if source == 'db':
        from api import create_app
        app = create_app()
        with app.app_context():
            articles = fetch_articles_from_db(date_str)
            from api.services.xhs_dedup import seen_source_urls
            seen = seen_source_urls()
    else:
        articles = fetch_articles_from_api(date_str)
        seen = seen_urls_from_output(OUTPUT_ROOT)

    logger.info(f"{date_str} 取到 {len(articles)} 篇")

    from api.services.xhs_dedup import filter_unpublished
    articles = filter_unpublished(articles, seen)
    logger.info(f"去重后剩余 {len(articles)} 篇")

    attach_source_text(articles)

    day_dir = OUTPUT_ROOT / date_str
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / INPUT_FILENAME
    path.write_text(
        json.dumps({'date': date_str, 'articles': articles}, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print(f"\n待选 {len(articles)} 篇 → {path}")
    print(f"排完序、写完文案后存成 {day_dir / NOTES_FILENAME}，再跑：")
    print(f"  python scripts/xhs/run_daily.py build --date {date_str}")
    return path


def cmd_build(date_str: str) -> Path:
    """第二段：读排好的文案，出图并渲染审核页。"""
    import image_finder
    import render

    day_dir = OUTPUT_ROOT / date_str
    articles = json.loads((day_dir / INPUT_FILENAME).read_text(encoding='utf-8'))['articles']
    picks = json.loads((day_dir / NOTES_FILENAME).read_text(encoding='utf-8'))['picks']

    picks = [
        {**pick, 'note': normalize_note(pick['note'])}
        for pick in picks if pick.get('note')
    ]
    logger.info(f"读到 {len(picks)} 篇已排好的文案")

    # 只给选中的这几篇补抓配图，别为 14 篇全都发一遍请求
    picked_urls = {p['url'] for p in picks}
    for article in articles:
        if article.get('url') in picked_urls and not article.get('image_url'):
            article['image_url'] = image_finder.backfill_image(article)

    result = run_pipeline(
        articles,
        PreparedScorer(picks),
        PreparedCopywriter(picks),
        render.render_note,
        OUTPUT_ROOT,
        date_str,
    )

    for candidate in result['candidates']:
        write_note_json(candidate)

    review_path = render_review_page(result, day_dir / 'review.html')
    print(f"\n候选 {len(result['candidates'])} 篇，失败 {len(result['failures'])} 篇")
    print(f"审核页：file://{review_path}")
    return review_path


def cmd_auto(date_str: str) -> Path:
    """一段跑完的全自动路径，用 DeepSeek 打分和写文案。需要 DEEPSEEK_API_KEY。"""
    from api import create_app
    from api.models.article import DailyNewsletter
    from api.models.xhs_post import STATUS_DRAFTED, XhsPost
    from api.services.xhs_copywriter import XhsCopywriterService
    from api.services.xhs_dedup import filter_unpublished, seen_source_urls
    from api.services.xhs_scorer import XhsScorerService
    from config import Config

    import render

    app = create_app()
    with app.app_context():
        today = datetime.strptime(date_str, '%Y-%m-%d').date()

        # 同一天重跑：先清掉今天还没发出去的草稿记录，否则去重会把它们当"已出稿"
        # 全部滤掉，重跑只会得到一张空的审核页。已发布和已丢弃的记录不动。
        discarded = XhsPost.objects(source_date=today, status=STATUS_DRAFTED).delete()
        if discarded:
            logger.info(f"重跑：清理今天的 {discarded} 条草稿记录")

        newsletter = DailyNewsletter.objects(date=today).first()
        articles = flatten_sections(newsletter.sections) if newsletter else []
        logger.info(f"{date_str} 当天文章 {len(articles)} 篇")

        articles = filter_unpublished(articles, seen_source_urls())
        logger.info(f"去重后剩余 {len(articles)} 篇")

        api_key = Config.DEEPSEEK_API_KEY
        result = run_pipeline(
            articles,
            XhsScorerService(api_key),
            XhsCopywriterService(api_key),
            render.render_note,
            OUTPUT_ROOT,
            date_str,
        )

        for candidate in result['candidates']:
            write_note_json(candidate)
            try:
                XhsPost(
                    source_url=candidate['source_url'],
                    source_date=today,
                    source_title=candidate['source_title'],
                    title=candidate['note'].get('title'),
                    body=candidate['note'].get('body'),
                    tags=candidate['note'].get('tags', []),
                    output_dir=str(candidate['out_dir']),
                ).save()
            except Exception as e:
                # 出稿记录写失败不该让整批白跑——图和文案已经落盘了，
                # 代价只是这条新闻明天可能再被选一次。
                logger.error(f"第 {candidate['index']} 条出稿记录写入失败：{str(e)}")

        review_path = render_review_page(
            result, OUTPUT_ROOT / date_str / 'review.html'
        )

    print(f"\n候选 {len(result['candidates'])} 篇，失败 {len(result['failures'])} 篇")
    print(f"审核页：file://{review_path}")
    return review_path


def main():
    parser = argparse.ArgumentParser(
        description='小红书每日流水线。prepare 取新闻，build 出图，auto 用 DeepSeek 一段跑完。'
    )
    parser.add_argument('command', choices=['prepare', 'build', 'auto'])
    parser.add_argument('--date', default=None, help='YYYY-MM-DD，默认取美东当天')
    parser.add_argument(
        '--source', choices=['api', 'db'], default='api',
        help='prepare 的数据来源：api 走公开接口（无需数据库凭据），db 走 MongoDB'
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    date_str = args.date or today_eastern()

    if args.command == 'prepare':
        cmd_prepare(date_str, args.source)
    elif args.command == 'build':
        cmd_build(date_str)
    else:
        cmd_auto(date_str)


if __name__ == '__main__':
    main()
