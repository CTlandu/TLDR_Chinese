import logging
from typing import List, Dict, Optional
import os
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

class TitleGeneratorService:
    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        初始化文心一言服务
        :param api_key: 百度智能云 API Key
        :param secret_key: 百度智能云 Secret Key
        """
        self.api_key = api_key or os.environ.get('ERNIE_API_KEY')
        self.secret_key = secret_key or os.environ.get('ERNIE_SECRET_KEY')
        self.access_token = None
        
    def _get_access_token(self) -> str:
        """获取百度智能云 access token"""
        url = f"https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params)
            result = response.json()
            if 'access_token' in result:
                return result['access_token']
            else:
                raise Exception(f"获取 access token 失败: {result}")
        except Exception as e:
            logging.error(f"获取 access token 出错: {str(e)}")
            raise
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_title(self, articles: List[Dict]) -> Optional[str]:
        """根据文章内容生成标题"""
        try:
            logging.info("开始生成标题...")
            
            # 如果没有 access token 则获取
            if not self.access_token:
                self.access_token = self._get_access_token()
            
            # 提取最重要的3-5个文章标题
            titles = []
            for section in articles:
                if section['section'] in ['Big Tech & Startups', 'Science & Futuristic Technology']:
                    for article in section['articles'][:2]:
                        titles.append(article['title'])
            
            # 只取前5个标题
            titles = titles[:5]
            logging.info(f"已提取 {len(titles)} 个标题")
            
            # 构建 prompt
            prompt = f"""
            你是一个专业的科技新闻编辑，请基于以下今日重要科技新闻:
            {' | '.join(titles)}
            
            生成一个吸引眼球的中文邮件主题，要求：
            1. 必须以"TLDR科技日报："开头
            2. 总长度控制在65字符以内（包括开头的"TLDR科技日报："）
            3. 突出最重要或最有趣的1-2个新闻点
            4. 使用数字或关键词增加吸引力
            5. 避免标题党，保持专业性
            6. 在结尾增加适当的表情符号
            
            直接返回生成的标题，不要包含任何解释或其他内容。
            """
            
            # 调用文心一言 API
            url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
            headers = {
                'Content-Type': 'application/json'
            }
            params = {
                'access_token': self.access_token
            }
            payload = {
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7,
                'top_p': 0.8
            }
            
            logging.info("正在调用文心一言 API...")
            response = requests.post(url, headers=headers, params=params, json=payload)
            result = response.json()
            
            if 'result' in result:
                title = result['result'].strip()
                logging.info(f"生成的标题: {title}")
                
                # 验证标题格式和长度
                if not title.startswith("TLDR科技日报："):
                    title = "TLDR科技日报：" + title
                
                if len(title) > 65:
                    title = title[:62] + "..."
                    
                return title
            else:
                raise Exception(f"API 调用失败: {result}")
            
        except Exception as e:
            logging.error(f"Title generation error: {str(e)}")
            return "TLDR科技日报：今日科技要闻速递 🚀"  # 默认标题 