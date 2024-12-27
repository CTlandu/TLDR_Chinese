from bs4 import BeautifulSoup
import requests
import pytz
from datetime import datetime
from functools import lru_cache
import time
from ..services.translator import TranslatorService
from ..services.image_extractor import extract_article_image
from flask import current_app
from ..models.article import DailyNewsletter
import logging
import json
import os
from ..services.title_generator import TitleGeneratorService

def get_newsletter(date=None):
    """
    获取每日新闻简报
    :param date: 日期字符串，格式为 YYYY-MM-DD
    :return: 包含 sections 和 generated_title 的字典
    """
    try:
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
        
        if not date:
            date = now_et.strftime('%Y-%m-%d')
        
        # 将输入的日期转换为美东时间的日期对象
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_obj_et = et.localize(date_obj)
        date_obj_et = date_obj_et.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 添加详细日志
        logging.info(f"请求日期: {date}")
        logging.info(f"当前美东时间日期: {now_et.date()}")
        logging.info(f"转换为美东时间日期: {date_obj_et.date()}")
        
        # 检查是否是未来日期（相对于美东时间）
        if date_obj_et.date() > now_et.date():
            logging.warning(f"请求的未来日期: {date} ET, 返回最新可用简报")
            latest_newsletter = DailyNewsletter.objects().order_by('-date').first()
            if latest_newsletter:
                logging.info(f"Found latest newsletter from: {latest_newsletter.date}")
                return {
                    'sections': latest_newsletter.sections,
                    'generated_title': latest_newsletter.generated_title
                }
            logging.warning("数据库中没有简报")
            return None
            
        # 首先查找数据库中请求的日期（使用美东时间的日期）
        newsletter = DailyNewsletter.objects(date=date_obj_et.date()).first()
        if newsletter:
            logging.info(f"Found newsletter in database for {date} ET")
            return {
                'sections': newsletter.sections,
                'generated_title': newsletter.generated_title
            }
            
        # 如果数据库中没有，尝试从源站获取
        logging.info(f"Newsletter not found in database, fetching from source for {date} ET")
        articles = fetch_tldr_content(date)
        
        if not articles:
            logging.warning(f"No content available for date: {date} ET, trying to get latest available")
            latest_newsletter = DailyNewsletter.objects().order_by('-date').first()
            if latest_newsletter:
                logging.info(f"Returning latest available newsletter from: {latest_newsletter.date}")
                # 返回完整的信息，包括 sections 和 generated_title
                return {
                    'sections': latest_newsletter.sections,
                    'generated_title': latest_newsletter.generated_title
                }
            return None
            
        # 如果获取到了内容，保存到数据库（使用美东时间的日期）
        try:
            if articles:
                newsletter = DailyNewsletter(
                    date=date_obj_et.date(),
                    sections=articles['sections'],
                    generated_title=articles['generated_title']  # 保存生成的标题
                )
                newsletter.save()
                logging.info(f"Successfully saved newsletter with title to database for {date} ET")
                return {
                    'sections': articles['sections'],
                    'generated_title': articles['generated_title']
                }
                
        except Exception as e:
            logging.error(f"Database save error: {str(e)}")
            if articles:
                return {
                    'sections': articles['sections'],
                    'generated_title': articles['generated_title']
                }
            return None
            
    except Exception as e:
        logging.error(f"Error in get_newsletter: {str(e)}")
        return None

def fetch_tldr_content(date):
    url = f"https://tldr.tech/tech/{date}"
    logging.info(f"Fetching content from: {url}")
    
    try:
        response = requests.get(url, timeout=10)  # 添加超时设置
        logging.info(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            logging.warning(f"Failed to fetch content: HTTP {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        sections = soup.find_all('section')
        if not sections:
            logging.warning("No sections found in the page")
            return None
            
        logging.info(f"Found {len(sections)} sections")
        
        for section in sections:
            header = section.find('h3', class_='text-center font-bold')
            if not header:
                continue
                
            section_title = header.text.strip()
            if "sponsor" in section_title.lower():
                continue
                
            logging.info(f"Processing section: {section_title}")
            section_content = []
            
            for article in section.find_all('article', class_='mt-3'):
                try:
                    title_elem = article.find('h3')
                    if not title_elem or "sponsor" in title_elem.text.lower():
                        continue
                        
                    title = title_elem.text.strip()
                    translator = TranslatorService(current_app.config['DEEPL_API_KEY'])
                    
                    content = article.find('div', class_='newsletter-html')
                    content_html = ''.join(str(tag) for tag in content.contents) if content else ""
                    
                    # 翻译标题和内容
                    title_zh = translator.translate_to_chinese(title)
                    content_html_zh = translator.translate_to_chinese(content_html)
                    
                    link = article.find('a', class_='font-bold')
                    url = link['href'] if link else ""
                    
                    # 提取文章图片
                    image_url = extract_article_image(url) if url else None
                    
                    article_content = {
                        'title': title_zh,
                        'title_en': title,
                        'content': content_html_zh,
                        'content_en': content_html,
                        'url': url,
                        'image_url': image_url
                    }
                    section_content.append(article_content)
                    logging.info(f"Processed article: {title}")
                    
                except Exception as e:
                    logging.error(f"Error processing article: {str(e)}")
                    continue
            
            if section_content:
                articles.append({
                    'section': section_title,
                    'articles': section_content
                })
        
        if not articles:
            logging.warning("No valid articles found")
            return None
            
        try:
            # 在所有文章处理完成后，生成标题
            if articles:
                # 初始化标题生成器
                title_generator = TitleGeneratorService(
                    os.environ.get('ERNIE_API_KEY'),
                    os.environ.get('ERNIE_SECRET_KEY')
                )
                
                # 生成标题
                generated_title = title_generator.generate_title(articles)
                logging.info(f"生成的标题: {generated_title}")
                
                # 返回带有标题的文章数据
                return {
                    'sections': articles,
                    'generated_title': generated_title
                }
                
            return None
            
        except Exception as e:
            logging.error(f"Error fetching content: {str(e)}")
            return None
        
    except requests.RequestException as e:
        logging.error(f"Request error: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error fetching content: {str(e)}")
        return None
