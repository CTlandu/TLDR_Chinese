import sys
import os
import logging
from pathlib import Path
from api.services.title_generator import TitleGeneratorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ernie_api():
    """测试文心一言 API 是否正常工作"""
    # 1. 检查环境变量
    api_key = os.environ.get('ERNIE_API_KEY')
    secret_key = os.environ.get('ERNIE_SECRET_KEY')
    
    print("\n=== API Key 检查 ===")
    print(f"API Key: {api_key[:10] if api_key else 'None'}...")
    print(f"Secret Key: {secret_key[:10] if secret_key else 'None'}...")
    
    if not api_key or not secret_key:
        print("错误：未找到 ERNIE_API_KEY 或 ERNIE_SECRET_KEY 环境变量")
        return False
    
    try:
        # 初始化服务
        service = TitleGeneratorService(api_key, secret_key)
        
        # 测试获取 access token
        print("\n=== 测试获取 access token ===")
        access_token = service._get_access_token()
        print(f"Access Token: {access_token[:10]}...")
        
        # 测试生成标题
        print("\n=== 测试生成标题 ===")
        test_articles = [
            {
                'section': 'Big Tech & Startups',
                'articles': [
                    {'title': 'OpenAI releases GPT-4 with improved capabilities'},
                    {'title': 'Tesla announces new battery technology'}
                ]
            }
        ]
        
        title = service.generate_title(test_articles)
        print(f"\n生成的标题: {title}")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
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
    
    # 测试文心一言 API
    test_ernie_api()

if __name__ == "__main__":
    test_title_generation()