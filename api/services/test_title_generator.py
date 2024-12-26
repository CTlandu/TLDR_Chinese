import sys
import os
import google.generativeai as genai
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path
import logging
from api import create_app
from api.models.article import DailyNewsletter
from api.services.title_generator import TitleGeneratorService
import json
from datetime import datetime
import pytz
import dns.resolver
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_mongodb_dns():
    """设置 MongoDB DNS 解析器"""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '8.8.4.4']
    dns.resolver.default_resolver = resolver

def test_title_generation():
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    
    # 清除代理设置
    if 'HTTPS_PROXY' in os.environ:
        del os.environ['HTTPS_PROXY']
    if 'HTTP_PROXY' in os.environ:
        del os.environ['HTTP_PROXY']
    
    # 从项目根目录加载 .env.development
    ROOT_DIR = Path(__file__).parent.parent.parent
    from dotenv import load_dotenv
    env_path = os.path.join(ROOT_DIR, '.env.development')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"已加载配置文件: {env_path}")
        # 验证环境变量是否加载成功
        mongodb_uri = os.environ.get('MONGODB_URI')
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        logger.info(f"MONGODB_URI: {mongodb_uri and mongodb_uri[:20]}...")
        logger.info(f"GEMINI_API_KEY: {gemini_api_key and gemini_api_key[:10]}...")
        
        # 直接设置到 config 中
        from config import Config
        Config.MONGODB_SETTINGS['host'] = mongodb_uri
        Config.GEMINI_API_KEY = gemini_api_key
        
    else:
        logger.error(f"找不到配置文件: {env_path}")
        return
    
    # 设置 MongoDB DNS
    setup_mongodb_dns()
    
    # 创建应用上下文
    from config import DevelopmentConfig
    config = DevelopmentConfig()
    app = create_app(config)
    
    with app.app_context():
        # 检查数据库内容
        logger.info("检查数据库内容...")
        newsletters = DailyNewsletter.objects()
        count = newsletters.count()
        logger.info(f"数据库中共有 {count} 条 newsletter 记录")
        
        if count > 0:
            # 显示最新的一条记录
            latest = newsletters.order_by('-date').first()
            logger.info(f"最新记录日期: {latest.date}")
            logger.info(f"包含 {len(latest.sections)} 个板块")
            
        # 从环境变量获取API key
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            logger.error("未在配置中找到 GEMINI_API_KEY")
            return

        logger.info("使用 GEMINI_API_KEY: %s...", api_key[:10])
        
        # 配置 Gemini
        genai.configure(api_key=api_key)
        
        # 初始化服务
        title_generator = TitleGeneratorService(api_key)
        
        # 获取最近的几期newsletter进行测试
        test_newsletters = newsletters.order_by('-date')[:3]
        
        logger.info("\n=== 开始测试标题生成 ===\n")
        
        for newsletter in test_newsletters:
            try:
                date = newsletter.date.strftime('%Y-%m-%d')
                logger.info(f"\n日期: {date}")
                logger.info("原文标题:")
                for section in newsletter.sections[:2]:
                    for article in section['articles'][:2]:
                        logger.info(f"- {article['title']}")
                
                # 生成新标题，添加重试机制
                for attempt in range(3):  # 最多尝试3次
                    try:
                        title = title_generator.generate_title(newsletter.sections)
                        logger.info(f"\n生成的标题: {title}")
                        logger.info(f"标题长度: {len(title)} 字符")
                        break
                    except Exception as e:
                        if attempt == 2:  # 最后一次尝试
                            logger.error(f"生成标题失败: {str(e)}")
                            title = "TLDR科技日报：今日科技要闻速递 🚀"  # 使用默认标题
                        else:
                            logger.warning(f"第 {attempt+1} 次尝试失败，正在重试...")
                            continue
                
                logger.info("\n" + "="*50)
            except Exception as e:
                logger.error(f"处理 newsletter 时出错: {str(e)}")
                continue

if __name__ == "__main__":
    test_title_generation()