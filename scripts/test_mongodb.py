import sys
import os
from pathlib import Path
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import requests
import socket
import dns.resolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mongodb_client():
    """创建 MongoDB 客户端"""
    # 设置 DNS 解析器
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # 使用 Google DNS
    
    # 设置 MongoDB DNS 解析器
    dns.resolver.default_resolver = resolver
    
    uri = "mongodb+srv://colintangxy:CTlanduadmin123@tldrchinese.katwf.mongodb.net/?retryWrites=true&w=majority&appName=TLDRChinese"
    
    return MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        ssl=True,
        tlsInsecure=True,
        directConnection=False,
        connect=True,  # 强制立即连接
    )

def test_mongodb_connection():
    # 1. 测试代理连接
    try:
        proxy = os.environ.get('HTTPS_PROXY')
        logger.info(f"当前代理设置: {proxy}")
        
        response = requests.get('https://www.google.com', 
                              proxies={'http': proxy, 'https': proxy},
                              verify=False,
                              timeout=5)
        logger.info("Google 连接测试成功")
    except Exception as e:
        logger.error(f"代理测试失败: {str(e)}")
    
    # 2. 尝试连接 MongoDB
    try:
        logger.info("尝试连接 MongoDB...")
        client = create_mongodb_client()
        
        # 测试连接
        client.admin.command('ping')
        logger.info("MongoDB 连接成功！")
        
        # 测试数据库访问
        db = client.tldrchinese
        collections = db.list_collection_names()
        logger.info(f"可用的集合: {collections}")
        
    except ConnectionFailure as e:
        logger.error(f"MongoDB 连接失败: {str(e)}")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    
    # 从项目根目录加载 .env.development
    from dotenv import load_dotenv
    ROOT_DIR = Path(__file__).parent.parent.parent
    env_path = os.path.join(ROOT_DIR, '.env.development')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print(f"找不到配置文件: {env_path}")
    
    test_mongodb_connection() 