from bs4 import BeautifulSoup
import requests
import pytz
from datetime import datetime
from functools import lru_cache
import time
from ..services.translator import TranslatorService
from flask import current_app
from ..models.article import Article
import logging

@lru_cache(maxsize=128)
def get_newsletter(date=None, timestamp=None):
    if timestamp is None:
        timestamp = time.strftime('%Y%m%d')
    return fetch_tldr_content(date)

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
                    
                    logging.info(f"Processed article: {title}")
                    
                    # 构建双语内容
                    article_content = f"""### [{title_zh}]({url})
> {title}

{content_html_zh}

<blockquote class="original-text">
{content_html}
</blockquote>

---"""
                    section_content.append(article_content)
                
                if section_content:
                    articles.append({
                        'section': section_title,
                        'content': ''.join(section_content)
                    })
            
            logging.info(f"Returning {len(articles)} articles")
            return articles
            
    except Exception as e:
        logging.error(f"Error fetching content: {str(e)}")
        return []
