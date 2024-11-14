from flask import Blueprint, jsonify
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
    response.headers.add('Access-Control-Allow-Origin', 'https://www.tldrnewsletter.cn')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
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
    
    articles = get_newsletter(date)
    if not articles:
        # 尝试从源获取数据
        articles = fetch_tldr_content(date)
        if articles:
            # 如果成功获取数据，更新数据库
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            newsletter = DailyNewsletter(date=date_obj, sections=articles)
            newsletter.save()
        else:
            # 如果没有数据，获取数据库中最新一天的新闻
            available_dates = get_available_dates()
            for available_date in available_dates:
                articles = get_newsletter(available_date)
                if articles:
                    date = available_date
                    break

    processed_articles = []
    for section in articles:
        processed_section = {
            'section': get_section_emoji(section['section']),
            'articles': []
        }
        
        for article in section['articles']:
            processed_article = article.copy()
            processed_article['title'] = get_title_emoji(article['title'])
            processed_section['articles'].append(processed_article)
            
        processed_articles.append(processed_section)
    
    response = {
        'articles': processed_articles,
        'currentDate': date,
        'dates': get_available_dates()
    }
    
    return jsonify(response)

@bp.route('/api/wechat/newsletter/<date>')
def get_wechat_newsletter(date):
    articles = get_newsletter(date)
    
    # 处理文章内容
    processed_articles = []
    for section in articles:
        processed_section = {
            'section': get_section_emoji(section['section']),
            'articles': []
        }
        
        for article in section['articles']:
            processed_article = article.copy()
            # 清理标题中的阅读时间
            processed_article['title'] = clean_reading_time(article['title'])
            processed_article['title_en'] = clean_reading_time(article['title_en'])
            # 添加标题 emoji
            processed_article['title'] = get_title_emoji(processed_article['title'])
            processed_section['articles'].append(processed_article)
            
        processed_articles.append(processed_section)
    
    response = {
        'articles': processed_articles,
        'currentDate': date
    }
    
    return jsonify(response)

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