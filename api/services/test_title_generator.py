import sys
import os
from pathlib import Path
import logging
from datetime import datetime, timedelta
import dns.resolver

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from api.services.title_generator import TitleGeneratorService
from api.models.article import DailyNewsletter
from api import create_app
from config import Config  # 导入配置类
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_dns():
    """设置 DNS 解析器"""
    try:
        # 使用 Google 的 DNS 服务器
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        dns.resolver.default_resolver = resolver
        logger.info("DNS 解析器配置成功")
        return True
    except Exception as e:
        logger.error(f"DNS 解析器配置失败: {str(e)}")
        return False

def load_environment():
    """加载环境变量"""
    env_path = os.path.join(ROOT_DIR, '.env.development')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"已加载配置文件: {env_path}")
        mongodb_uri = os.environ.get('MONGODB_URI')
        if mongodb_uri:
            logger.info(f"MongoDB URI: {mongodb_uri[:20]}...")
            return True
        else:
            logger.error("未找到 MongoDB URI")
            return False
    else:
        logger.error(f"找不到配置文件: {env_path}")
        return False

def test_multiple_days():
    """测试最近三天的新闻标题生成"""
    try:
        # 确保环境变量和DNS设置
        if not setup_dns() or not load_environment():
            return False
            
        os.environ['FLASK_ENV'] = 'development'
        config = Config()
        app = create_app(config)
        
        with app.app_context():
            logger.info("正在连接数据库...")
            
            # 获取最近三天的 newsletters
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3)
            
            newsletters = DailyNewsletter.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            ).order_by('-date')
            
            logger.info(f"找到 {newsletters.count()} 天的新闻")
            
            for newsletter in newsletters:
                logger.info(f"\n=== 处理 {newsletter.date.strftime('%Y-%m-%d')} 的新闻 ===")
                
                # 准备文章数据
                articles = []
                for section in newsletter.sections:
                    if section['section'] in ['Big Tech & Startups', 
                                            'Science & Futuristic Technology',
                                            'Miscellaneous']:
                        articles.append({
                            'section': section['section'],
                            'articles': [
                                {'title': article['title']}
                                for article in section['articles']
                            ]
                        })
                
                # 生成标题
                api_key = os.environ.get('ERNIE_API_KEY')
                secret_key = os.environ.get('ERNIE_SECRET_KEY')
                
                if not api_key or not secret_key:
                    logger.error("未找到 API Key 或 Secret Key")
                    return False
                
                service = TitleGeneratorService(api_key, secret_key)
                title = service.generate_title(articles)
                
                logger.info(f"生成的标题: {title}")
                logger.info("=" * 80 + "\n")
                
            return True
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_multiple_days()