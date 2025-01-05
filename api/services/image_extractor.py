import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException
import urllib3

# 忽略 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_session():
    """创建一个带有重试机制的 session"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_article_image(url):
    """
    从文章URL中提取最相关的图片URL
    """
    if not url:
        return None
        
    try:
        session = create_session()
        response = session.get(
            url, 
            timeout=20,  # 增加超时时间
            verify=False,  # 禁用 SSL 验证
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        if response.status_code != 200:
            logging.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 优先级顺序查找图片
        # 1. Open Graph 图片
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            logging.info(f"Found og:image for {url}: {og_image['content']}")
            return og_image['content']
            
        # 2. Twitter Card 图片
        twitter_image = soup.find('meta', property='twitter:image')
        if twitter_image and twitter_image.get('content'):
            logging.info(f"Found twitter:image for {url}: {twitter_image['content']}")
            return twitter_image['content']
            
        # 3. 文章主体中的第一张图片
        article_tag = soup.find(['article', 'main', '.post-content', '.article-content'])
        if article_tag:
            first_image = article_tag.find('img')
            if first_image and first_image.get('src'):
                image_url = urljoin(url, first_image['src'])
                logging.info(f"Found article image for {url}: {image_url}")
                return image_url
                
        # 4. 页面中任何看起来像文章图片的图片
        images = soup.find_all('img')
        for img in images:
            src = img.get('src')
            if src and any(keyword in src.lower() for keyword in ['article', 'post', 'feature', 'main', 'hero']):
                image_url = urljoin(url, src)
                logging.info(f"Found potential article image for {url}: {image_url}")
                return image_url
                
        logging.warning(f"No suitable image found for {url}")
        return None
        
    except RequestException as e:
        logging.error(f"Error extracting image from {url}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error extracting image from {url}: {str(e)}")
        return None