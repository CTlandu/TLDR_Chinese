from flask import Blueprint, jsonify, request
from .services.newsletter import get_newsletter, fetch_tldr_content
from datetime import datetime
import pytz
from datetime import timedelta
from .services.emoji_mapper import get_section_emoji, clean_reading_time, get_title_emoji
from .models.article import DailyNewsletter
import logging
from flask import make_response



bp = Blueprint('main', __name__)


# 添加在文件开头的导入语句之后，但在所有路由之前
@bp.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed_origins = [
        'https://www.tldrnewsletter.cn',
        'http://localhost:5173',  # 添加本地开发环境
        'http://localhost:3000',
        'https://tldrnewsletter.cn',
        'https://tldr-chinese-frontend.onrender.com',
        'https://tldr-chinese-backend.onrender.com',
        # 如果你使用其他端口也可以添加
    ]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'false')
    return response

def get_available_dates(days=7):
    et = pytz.timezone('US/Eastern')
    dates = []
    current = datetime.now(et)
    
    for i in range(days):
        date = current - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    return dates

@bp.route('/api/newsletter/<date>')
def get_newsletter_by_date(date):
    try:
        articles = get_newsletter(date)
        
        if not articles:
            return jsonify({
                'articles': [],
                'currentDate': date,
                'dates': get_available_dates()
            }), 200
            
        # 获取实际返回的文章日期
        actual_date = date
        if DailyNewsletter.objects(sections=articles).first():
            actual_date = DailyNewsletter.objects(sections=articles).first().date.strftime('%Y-%m-%d')
            
        processed_articles = []
        for section in articles:
            if not isinstance(section, dict) or 'section' not in section:
                continue
                
            processed_section = {
                'section': get_section_emoji(section['section']),
                'articles': []
            }
            
            if 'articles' in section and isinstance(section['articles'], list):
                for article in section['articles']:
                    if isinstance(article, dict):
                        processed_article = article.copy()
                        if 'title' in processed_article:
                            processed_article['title'] = get_title_emoji(article['title'])
                        processed_section['articles'].append(processed_article)
            
            processed_articles.append(processed_section)
        
        return jsonify({
            'articles': processed_articles,
            'currentDate': actual_date,  # 返回实际的日期
            'dates': get_available_dates()
        })
            
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': '暂时无法获取新闻内容，请稍后再试',
            'articles': [],
            'currentDate': date,
            'dates': get_available_dates()
        }), 200

@bp.route('/api/wechat/newsletter/<date>')
def get_wechat_newsletter(date):
    try:
        articles = get_newsletter(date)
        if not articles:
            return jsonify({'error': 'No articles found'}), 404
        
        html_content = []
        html_content.append(f'<div style="margin-bottom: 20px; text-align: center; font-size: 20px; font-weight: bold;">TLDR每日科技新闻 【{date}】</div>')
        
        for section in articles:
            processed_section = get_section_emoji(section['section'])
            # 添加分区标题
            html_content.append(
                f'<div style="margin: 20px 0; padding: 10px 0; font-size: 18px; font-weight: bold; border-bottom: 1px solid #e5e5e5;">'
                f'{processed_section}'
                f'</div>'
            )
            
            for article in section['articles']:
                # 清理和处理文章内容
                title = clean_reading_time(article['title'])
                title = get_title_emoji(title)
                content = article['content']
                url = article.get('url', '')
                image_url = article.get('image_url', '')
                
                # 构建文章 HTML
                article_html = [
                    # 文章容器
                    '<div style="margin-bottom: 25px;">',
                    
                    # 标题（中英双语）
                    f'<div style="font-size: 17px; font-weight: bold; margin-bottom: 10px; color: #333;">{title}</div>',
                    f'<div style="font-size: 15px; color: #666; margin-bottom: 10px;">{article["title_en"]}</div>',
                    
                    # 图片（如果有）
                    f'<img src="{image_url}" style="width: 100%; margin: 10px 0; border-radius: 4px;" />' if image_url else '',
                    
                    # 内容（中英双语）
                    f'<div style="font-size: 15px; line-height: 1.6; color: #333; margin: 10px 0;">{content}</div>',
                    f'<div style="font-size: 14px; line-height: 1.6; color: #666; margin: 10px 0;">{article["content_en"]}</div>',
                    
                    # 原文链接
                    f'<div style="font-size: 14px; color: #666; margin-top: 8px;">',
                    f'原文链接：<a href="{url}" style="color: #576b95; text-decoration: none;">{url}</a>',
                    '</div>',
                    
                    '</div>'  # 结束文章容器
                ]
                
                html_content.append(''.join(article_html))
        
        response = {
            'html': '\n'.join(html_content),
            'articles': [{
                'title': get_title_emoji(clean_reading_time(article['title'])),
                'title_en': article['title_en'],
                'content': article['content'],
                'content_en': article['content_en'],
                'url': article['url'],
                'image_url': article.get('image_url', ''),
                'section': get_section_emoji(section['section'])
            } for section in articles for article in section['articles']],
            'currentDate': date
        }
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error in get_wechat_newsletter: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/latest-articles')
def get_latest_articles():
    try:
        # 直接从数据库获取最新的一条记录
        latest_newsletter = DailyNewsletter.objects().order_by('-date').first()
        logging.info(f"Querying latest newsletter from database")
        
        if not latest_newsletter:
            logging.warning("No newsletters found in database")
            return jsonify([])
        
        latest_date = latest_newsletter.date.strftime('%Y-%m-%d')
        logging.info(f"Found latest newsletter from: {latest_date}")
        
        # 直接使用数据库中的文章数据
        flattened_articles = []
        for section in latest_newsletter.sections:
            processed_section = get_section_emoji(section['section'])
            logging.info(f"Processing section: {section['section']}")
            
            for article in section['articles']:
                processed_article = {
                    'title': get_title_emoji(clean_reading_time(article['title'])),
                    'title_en': clean_reading_time(article['title_en']),
                    'content': article['content'],
                    'content_en': article['content_en'],
                    'url': article['url'],
                    'image_url': article.get('image_url'),
                    'section': processed_section,
                    'date': latest_date
                }
                flattened_articles.append(processed_article)
        
        logging.info(f"Returning {len(flattened_articles)} articles")
        return jsonify(flattened_articles)
        
    except Exception as e:
        logging.error(f"Error in get_latest_articles: {str(e)}")
        return jsonify({'error': str(e)}), 500