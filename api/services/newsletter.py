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

@lru_cache(maxsize=128)
def get_newsletter(date=None):
    logging.info(f"Attempting to get newsletter for date: {date}")
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        if date_obj > datetime.now():
            logging.warning(f"Future date requested: {date}")
            return []
            
        newsletter = DailyNewsletter.objects(date=date_obj).first()
        if newsletter:
            logging.info(f"Found newsletter in database for {date}")
            return json.loads(json.dumps(newsletter.sections, ensure_ascii=False))
            
        logging.info(f"Newsletter not found in database, fetching from source")
        articles = fetch_tldr_content(date)
        if articles:
            try:
                newsletter = DailyNewsletter(
                    date=date_obj,
                    sections=articles
                )
                newsletter.save()
                logging.info(f"Successfully saved newsletter to database")
                return json.loads(json.dumps(articles, ensure_ascii=False))
            except Exception as e:
                logging.error(f"Database save error: {str(e)}")
                return articles
    except Exception as e:
        logging.error(f"Error in get_newsletter: {str(e)}")
        return []

def fetch_tldr_content(date=None):
    if date is None:
        et = pytz.timezone('US/Eastern')
        date = datetime.now(et).strftime('%Y-%m-%d')
    
    url = f"https://tldr.tech/tech/{date}"
    logging.info(f"Fetching content from: {url}")
    
    try:
        response = requests.get(url)
        logging.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            sections = soup.find_all('section')
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
                    title_elem = article.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    if "sponsor" in title.lower():
                        continue
                    
                    translator = TranslatorService(current_app.config['DEEPL_API_KEY'])
                    
                    content = article.find('div', class_='newsletter-html')
                    content_html = ''.join(str(tag) for tag in content.contents) if content else ""
                    
                    # 翻译标题和内容
                    title_zh = translator.translate_to_chinese(title)
                    content_html_zh = translator.translate_to_chinese(content_html)
                    
                    link = article.find('a', class_='font-bold')
                    url = link['href'] if link else ""
                    
                    # 提取文章图片
                    image_url = None
                    if url:
                        image_url = extract_article_image(url)
                        logging.info(f"Extracted image URL for article: {image_url}")
                    
                    logging.info(f"Processed article: {title}")
                    
                    # 构建双语内容，添加图片URL
                    article_content = {
                        'title': title_zh,
                        'title_en': title,
                        'content': content_html_zh,
                        'content_en': content_html,
                        'url': url,
                        'image_url': image_url
                    }
                    section_content.append(article_content)
                
                if section_content:
                    articles.append({
                        'section': section_title,
                        'articles': section_content
                    })
            
            logging.info(f"Returning {len(articles)} articles")
            return articles
            
        else:
            logging.warning(f"Failed to fetch content for date: {date}")
            return []
    except Exception as e:
        logging.error(f"Error fetching content: {str(e)}")
        return []
