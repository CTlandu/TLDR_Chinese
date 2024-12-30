import logging
from typing import List, Dict, Optional
import os
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

class TitleGeneratorService:
    def __init__(self, api_key: str = None, secret_key: str = None):
        """初始化文心一言服务"""
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
            
    def _extract_titles_by_section(self, articles: List[Dict]) -> Dict[str, List[str]]:
        """从各个版块提取中文标题"""
        section_titles = {
            'Big Tech & Startups': [],
            'Science & Futuristic Technology': [],
            'Miscellaneous': []
        }
        
        for section in articles:
            section_name = section['section']
            if section_name in section_titles:
                # 使用中文标题而不是英文标题
                titles = [article['title'] for article in section['articles']]
                section_titles[section_name] = titles
                
        return section_titles
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_title(self, articles: List[Dict]) -> Optional[str]:
        """根据文章内容生成标题"""
        try:
            logging.info("开始生成标题...")
            
            # 如果没有 access token 则获取
            if not self.access_token:
                self.access_token = self._get_access_token()
            
            # 提取各个版块的标题
            section_titles = self._extract_titles_by_section(articles)
            
            # 构建提供给 AI 的标题列表
            all_titles = []
            for section, titles in section_titles.items():
                if titles:  # 如果该版块有标题
                    all_titles.append(f"\n{section}:")
                    for i, title in enumerate(titles, 1):
                        all_titles.append(f"{i}. {title}")
            
            titles_text = "\n".join(all_titles)
            logging.info("提供给 AI 的标题列表：")
            logging.info(titles_text)
            
            # 改进的 prompt
            prompt = f"""
            你是一个专业的科技新闻编辑，请仔细阅读以下三个版块的科技新闻标题：

            {titles_text}

            请完成以下任务：
            1. 从所有新闻中选出2-3条最值得读者关注的新闻（考虑新闻的重要性、影响力和趣味性）
            2. 基于选中的新闻，生成一个引人注目的中文标题，要求：
               
               - 总长度尽可能接近65字符，但是不能超过65字符
               - 突出最重要或最有趣的2-3个新闻点
               - 使用数字或关键词增加吸引力
               - 新闻点之间使用"！"或"|"分隔
               - 标题示例：
                 * 重磅！亚马逊AI投资百亿美元！谷歌量子计算获重大突破 | OpenAI估值暴涨至800亿
                 * 突发！特斯拉新技术革命！英伟达AI芯片份额达90% | 微软推出重磅新品
                 * 刚刚！马斯克宣布：特斯拉将推出全新AI模型！苹果AI芯片将采用台积电3纳米工艺 | 微软推出重磅新品
               - 标题要有吸引力但保持专业性
               - 不要添加表情符号
            
            直接返回生成的标题，不要包含任何解释或其他内容。
            """
            
            # 调用文心一言 API
            url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
            headers = {'Content-Type': 'application/json'}
            params = {'access_token': self.access_token}
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
                

                
                if len(title) > 65:
                    title = title[:62] + "..."
                    
                return title
            else:
                raise Exception(f"API 调用失败: {result}")
            
        except Exception as e:
            logging.error(f"Title generation error: {str(e)}")
            return "TLDR科技日报：今日科技要闻速递"  # 默认标题 