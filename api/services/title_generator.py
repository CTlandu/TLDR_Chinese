import google.generativeai as genai
import logging
from typing import List, Dict, Optional
import os

class TitleGeneratorService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        
    def generate_title(self, articles: List[Dict]) -> Optional[str]:
        """根据文章内容生成标题"""
        try:
            logging.info("开始生成标题...")
            
            # 保存原始代理设置
            original_proxy = os.environ.get('HTTPS_PROXY')
            original_http_proxy = os.environ.get('HTTP_PROXY')
            original_all_proxy = os.environ.get('ALL_PROXY')
            
            # 临时清除所有代理设置
            proxy_vars = ['HTTPS_PROXY', 'HTTP_PROXY', 'ALL_PROXY', 'https_proxy', 'http_proxy', 'all_proxy']
            for var in proxy_vars:
                if var in os.environ:
                    del os.environ[var]
            
            logging.info("已清除代理设置")
            
            # 配置 Gemini
            logging.info(f"正在配置 Gemini，API Key: {self.api_key[:10]}...")
            genai.configure(api_key=self.api_key)
            if not self.model:
                self.model = genai.GenerativeModel('gemini-pro')
            logging.info("Gemini 配置完成")
            
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
            
            直接返回生��的标题，不要包含任何解释或其他内容。
            """
            
            logging.info("正在调用 Gemini API...")
            try:
                response = self.model.generate_content(prompt)
                logging.info("Gemini API 调用成功")
                title = response.text.strip()
                logging.info(f"生成的标题: {title}")
            except Exception as e:
                logging.error(f"Gemini API 调用失败: {str(e)}")
                raise
            
            # 验证标题格式和长度
            if not title.startswith("TLDR科技日报："):
                title = "TLDR科技日报：" + title
            
            if len(title) > 65:
                title = title[:62] + "..."
            
            # 恢复代理设置
            if original_proxy:
                os.environ['HTTPS_PROXY'] = original_proxy
            if original_http_proxy:
                os.environ['HTTP_PROXY'] = original_http_proxy
            if original_all_proxy:
                os.environ['ALL_PROXY'] = original_all_proxy
            
            logging.info("标题生成完成")
            return title
            
        except Exception as e:
            logging.error(f"Title generation error: {str(e)}")
            return "TLDR科技日报：今日科技要闻速递 🚀"  # 默认标题 