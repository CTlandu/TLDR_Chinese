import html as html_lib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

TOP_N = 3
OUTPUT_ROOT = SCRIPT_DIR / 'output'
REVIEW_TEMPLATE = SCRIPT_DIR / 'templates' / 'review.html'

TITLE_LIMIT = 20
BODY_LIMIT = 1000

logger = logging.getLogger(__name__)


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
            images = render_fn(note, out_dir, article.get('image_url'))
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


def main():
    import pytz

    from api import create_app
    from api.models.article import DailyNewsletter
    from api.models.xhs_post import XhsPost
    from api.services.xhs_copywriter import XhsCopywriterService
    from api.services.xhs_dedup import filter_unpublished, seen_source_urls
    from api.services.xhs_scorer import XhsScorerService
    from config import Config

    import render

    logging.basicConfig(level=logging.INFO)

    app = create_app()
    with app.app_context():
        eastern = pytz.timezone('US/Eastern')
        today = datetime.now(eastern).date()
        date_str = today.strftime('%Y-%m-%d')

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
            XhsPost(
                source_url=candidate['source_url'],
                source_date=today,
                source_title=candidate['source_title'],
                title=candidate['note'].get('title'),
                body=candidate['note'].get('body'),
                tags=candidate['note'].get('tags', []),
                output_dir=str(candidate['out_dir']),
            ).save()

        review_path = render_review_page(
            result, OUTPUT_ROOT / date_str / 'review.html'
        )

    print(f"\n候选 {len(result['candidates'])} 篇，失败 {len(result['failures'])} 篇")
    print(f"审核页：file://{review_path}")


if __name__ == '__main__':
    main()
