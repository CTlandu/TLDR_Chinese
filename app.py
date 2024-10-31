from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pytz
from functools import lru_cache
import time
from markdown import markdown
import bleach

app = Flask(__name__)

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown(text, extensions=['extra'])

def fetch_tldr_content(date=None):
    if date is None:
        et = pytz.timezone('US/Eastern')
        date = datetime.now(et).strftime('%Y-%m-%d')
    
    url = f"https://tldr.tech/tech/{date}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 获取所有文章部分
            sections = soup.find_all('section')
            for section in sections:
                # 获取部分标题
                header = section.find('h3', class_='text-center font-bold')
                if not header:
                    continue
                    
                section_title = header.text.strip()
                section_content = []
                
                # 获取该部分下的所有文章
                for article in section.find_all('article', class_='mt-3'):
                    title_elem = article.find('h3')
                    if not title_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    content = article.find('div', class_='newsletter-html')
                    content_text = content.text.strip() if content else ""
                    
                    link = article.find('a', class_='font-bold')
                    url = link['href'] if link else ""
                    
                    # 构建 Markdown 格式
                    article_md = f"### [{title}]({url})\n\n{content_text}\n\n"
                    section_content.append(article_md)
                
                if section_content:
                    articles.append({
                        'section': section_title,
                        'content': ''.join(section_content)
                    })
            
            return articles
    except Exception as e:
        print(f"Error fetching content: {str(e)}")
        return []

# 缓存 24 小时
@lru_cache(maxsize=128)
def fetch_tldr_content_cached(date, timestamp=None):
    if timestamp is None:
        timestamp = time.strftime('%Y%m%d')
    return fetch_tldr_content(date)

def get_newsletter(date=None):
    # 使用当前日期作为缓存key的一部分
    timestamp = time.strftime('%Y%m%d')
    return fetch_tldr_content_cached(date, timestamp)

@app.route('/')
@app.route('/newsletter')
def show_newsletter():
    et = pytz.timezone('US/Eastern')
    current_date = datetime.now(et).strftime('%Y-%m-%d')
    articles = get_newsletter()
    return render_template('emails.html', emails=articles, current_date=current_date)

@app.route('/newsletter/<date>')
def show_newsletter_by_date(date):
    articles = get_newsletter(date)
    return render_template('emails.html', emails=articles, current_date=date)

if __name__ == '__main__':
    app.run(debug=True)
