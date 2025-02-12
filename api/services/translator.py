import time
from functools import lru_cache
import logging
from openai import OpenAI

class TranslatorService:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def translate_title(self, title: str) -> str:
        """
        专门用于翻译标题的方法
        """
        try:
            # Log original title
            logging.info(f"开始翻译标题: {title}")
            
            # 检查是否包含 "minute read" 并标准化翻译
            title = self._standardize_minute_read(title)
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的翻译专家。请遵循以下规则：
1. 严格按照原文内容翻译标题，不要添加任何推测或补充的信息
2. 保持标题简洁明了，与原文长度相当
3. 保持新闻标题的简洁性，不要扩充解释
4. 如果不确定某个词的含义，保持原文
5. 使用地道的中文表达，但不要过度诠释
6. 直接返回翻译结果，不要添加任何说明文字"""
                    },
                    {
                        "role": "user",
                        "content": f"请直接翻译这个标题：\n\n{title}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            translated_title = response.choices[0].message.content.strip()
            # Log translated title
            logging.info(f"翻译结果: {translated_title}")
            
            return translated_title
            
        except Exception as e:
            logging.error(f"标题翻译错误 - 原文: {title}")
            logging.error(f"错误信息: {str(e)}")
            return title
            
    def translate_content(self, content: str) -> str:
        """
        专门用于翻译内容的方法
        """
        try:
            # Log original content (truncated for readability)
            content_preview = content[:100] + "..." if len(content) > 100 else content
            logging.info(f"开始翻译内容: {content_preview}")
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的翻译专家。请遵循以下规则：
1. 严格按照原文内容翻译，不要添加任何推测或补充的信息
2. 保持翻译简洁明了，与原文长度相当
3. 如果不确定某个词的含义，保持原文
4. 使用地道的中文表达，但不要过度诠释
5. 直接返回翻译结果，不要添加任何说明文字"""
                    },
                    {
                        "role": "user",
                        "content": f"请直接翻译这段内容：\n\n{content}"
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translated_content = response.choices[0].message.content.strip()
            # Log translated content (truncated for readability)
            translated_preview = translated_content[:100] + "..." if len(translated_content) > 100 else translated_content
            logging.info(f"翻译结果: {translated_preview}")
            
            return translated_content
            
        except Exception as e:
            logging.error(f"内容翻译错误 - 原文预览: {content_preview}")
            logging.error(f"错误信息: {str(e)}")
            return content
    
    def _standardize_minute_read(self, text):
        """
        标准化处理 "minute read" 的表达
        """
        import re
        # 匹配 (n minute read) 或 (n minutes read) 的模式
        pattern = r'\((\d+) minute[s]? read\)'
        
        def replace_minute_read(match):
            minutes = match.group(1)
            return f"（阅读时长{minutes}分钟）"
            
        return re.sub(pattern, replace_minute_read, text)
