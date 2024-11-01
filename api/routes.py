from flask import Blueprint, render_template, jsonify
from .services.newsletter import get_newsletter
from datetime import datetime
import pytz
from datetime import timedelta
from flask_cors import CORS
from .services.emoji_mapper import get_section_emoji, clean_reading_time, get_title_emoji


bp = Blueprint('main', __name__)

def get_available_dates(days=7):
    et = pytz.timezone('US/Eastern')
    dates = []
    current = datetime.now(et)
    
    for i in range(days):
        date = current - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    return dates

@bp.route('/')

@bp.route('/api/newsletter/<date>')
def get_newsletter_by_date(date):
    articles = get_newsletter(date)
    dates = get_available_dates()
    
    # 处理文章内容
    processed_articles = []
    for section in articles:
        # 创建新的 section 对象，避免修改原始数据
        processed_section = {
            'section': get_section_emoji(section['section']),
            'articles': []
        }
        
        for article in section['articles']:
            processed_article = article.copy()  # 创建文章的副本
            processed_article['title'] = get_title_emoji(article['title'])
            processed_section['articles'].append(processed_article)
            
        processed_articles.append(processed_section)
    
    response = {
        'articles': processed_articles,
        'currentDate': date,
        'dates': dates
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
