import google.generativeai as genai
import logging
from typing import List, Dict, Optional

class TitleGeneratorService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_title(self, articles: List[Dict]) -> Optional[str]:
        """根据文章内容生成标题"""
        try:
            # 提取最重要的3-5个文章标题
            titles = []
            for section in articles:
                if section['section'] in ['Big Tech & Startups', 'Science & Futuristic Technology']:
                    for article in section['articles'][:2]:
                        titles.append(article['title'])
            
            # 只取前5个标题
            titles = titles[:5]
            
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
            
            response = self.model.generate_content(prompt)
            title = response.text.strip()
            
            # 验证标题格式和长度
            if not title.startswith("TLDR科技日报："):
                title = "TLDR科技日报：" + title
            
            if len(title) > 65:
                title = title[:62] + "..."
                
            return title
            
        except Exception as e:
            logging.error(f"Title generation error: {str(e)}")
            return "TLDR科技日报：今日科技要闻速递 🚀"  # 默认标题 