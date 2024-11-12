import sys
import os
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import create_app
from api.models.article import DailyNewsletter
from api.services.image_extractor import extract_article_image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_articles_with_images():
    app = create_app()
    with app.app_context():
        # 获取所有newsletter
        newsletters = DailyNewsletter.objects()
        
        for newsletter in newsletters:
            logger.info(f"Processing newsletter for date: {newsletter.date}")
            modified = False
            
            for section in newsletter.sections:
                for article in section['articles']:
                    if 'image_url' not in article:
                        url = article.get('url')
                        if url:
                            logger.info(f"Extracting image for article: {article['title']}")
                            image_url = extract_article_image(url)
                            if image_url:
                                article['image_url'] = image_url
                                modified = True
                                logger.info(f"Added image URL: {image_url}")
            
            if modified:
                newsletter.save()
                logger.info(f"Updated newsletter for date: {newsletter.date}")

if __name__ == "__main__":
    update_articles_with_images()