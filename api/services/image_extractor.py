import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
import os

# 确保环境中没有代理设置
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('HTTP_PROXY', None)

def extract_article_image(url):
    """
    从文章URL中提取最相关的图片URL
    """
    try:
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 直接请求，不使用代理
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
            verify=True
        )
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 优先级顺序查找图片
        # 1. Open Graph 图片
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
            
        # 2. Twitter Card 图片
        twitter_image = soup.find('meta', property='twitter:image')
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
            
        # 3. 文章主体中的第一张图片
        article_tag = soup.find(['article', 'main', '.post-content', '.article-content'])
        if article_tag:
            first_image = article_tag.find('img')
            if first_image and first_image.get('src'):
                return urljoin(url, first_image['src'])
                
        # 4. 页面中任何看起来像文章图片的图片
        images = soup.find_all('img')
        for img in images:
            src = img.get('src')
            if src and any(keyword in src.lower() for keyword in ['article', 'post', 'feature', 'main', 'hero']):
                return urljoin(url, src)
                
        return None
        
    except Exception as e:
        logging.error(f"Error extracting image from {url}: {str(e)}")
        return None