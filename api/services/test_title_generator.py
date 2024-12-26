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

def test_network_connection():
    """测试网络连接"""
    logger.info("开始测试网络连接...")
    
    # 1. 测试基本网络连接
    try:
        response = requests.get('https://www.google.com', timeout=5)
        logger.info(f"Google 连接测试: 成功 (状态码: {response.status_code})")
    except Exception as e:
        logger.error(f"Google 连接测试失败: {str(e)}")
    
    # 2. 测试 Gemini API 连接
    try:
        # 清除代理设置
        proxy_vars = ['HTTPS_PROXY', 'HTTP_PROXY', 'ALL_PROXY', 'https_proxy', 'http_proxy', 'all_proxy']
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]
                
        response = requests.get('https://generativelanguage.googleapis.com/v1beta/models', 
                              timeout=5)
        logger.info(f"Gemini API 连接测试: 成功 (状态码: {response.status_code})")
    except Exception as e:
        logger.error(f"Gemini API 连接测试失败: {str(e)}")

def test_gemini_api():
    """测试 Gemini API 是否正常工作"""
    import google.generativeai as genai
    import requests
    
    # 1. 检查环境变量
    api_key = os.environ.get('GEMINI_API_KEY')
    print("\n=== API Key 检查 ===")
    print(f"从环境变量读取的 API Key: {api_key[:10] if api_key else 'None'}...")
    
    # 2. 直接从 .env.development 文件读取
    ROOT_DIR = Path(__file__).parent.parent.parent
    env_path = os.path.join(ROOT_DIR, '.env.development')
    print(f"\n=== 配置文件检查 ===")
    print(f"配置文件路径: {env_path}")
    print(f"配置文件是否存在: {os.path.exists(env_path)}")
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            print("\n配置文件内容预览:")
            for line in content.split('\n'):
                if 'GEMINI_API_KEY' in line:
                    key_value = line.split('=')[1] if '=' in line else 'NOT_FOUND'
                    print(f"GEMINI_API_KEY={key_value[:10]}...")
    
    if not api_key:
        print("\n错误：未找到 GEMINI_API_KEY 环境变量")
        return False
    
    try:
        print("\n=== Gemini API 测试 ===")
        # 清除所有代理设置
        proxy_vars = ['HTTPS_PROXY', 'HTTP_PROXY', 'ALL_PROXY', 'https_proxy', 'http_proxy', 'all_proxy']
        original_proxies = {}
        for var in proxy_vars:
            if var in os.environ:
                original_proxies[var] = os.environ[var]
                del os.environ[var]
        
        # 配置 Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        print(f"Gemini 响应: {response.text}")
        
        # 恢复代理设置
        for var, value in original_proxies.items():
            os.environ[var] = value
            
        return True
    except Exception as e:
        print(f"Gemini API 测试失败: {str(e)}")
        return False

def test_title_generation():
    # 确保环境变量设置
    os.environ['FLASK_ENV'] = 'development'
    
    # 从项目根目录加载 .env.development
    ROOT_DIR = Path(__file__).parent.parent.parent
    from dotenv import load_dotenv
    env_path = os.path.join(ROOT_DIR, '.env.development')
    
    print("\n=== 环境变量加载 ===")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"已加载配置文件: {env_path}")
    else:
        print(f"错误：找不到配置文件: {env_path}")
        return
    
    # 测试 Gemini API
    if not test_gemini_api():
        logger.error("Gemini API 测试失败，请检查 API Key")
        return
        
    # 先测试网络连接
    test_network_connection()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    
    # 保存原始代理设置
    original_proxy = os.environ.get('HTTPS_PROXY')
    original_http_proxy = os.environ.get('HTTP_PROXY')
    original_all_proxy = os.environ.get('ALL_PROXY')
    
    # 清除所有代理设置
    proxy_vars = ['HTTPS_PROXY', 'HTTP_PROXY', 'ALL_PROXY', 'https_proxy', 'http_proxy', 'all_proxy']
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
    
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
                            logger.warning(f"�� {attempt+1} 次尝试失败，正在重试...")
                            continue
                
                logger.info("\n" + "="*50)
            except Exception as e:
                logger.error(f"处理 newsletter 时出错: {str(e)}")
                continue

if __name__ == "__main__":
    test_title_generation()