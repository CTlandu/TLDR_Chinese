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
    
    @lru_cache(maxsize=128)
    def translate_to_chinese(self, text, timestamp=None):
        if timestamp is None:
            timestamp = time.strftime('%Y%m%d')
            
        try:
            # 检查是否包含 "minute read" 并标准化翻译
            text = self._standardize_minute_read(text)
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的翻译专家。请遵循以下规则：
1. 严格按照原文内容翻译，不要添加任何推测或补充的信息
2. 保持翻译简洁明了，与原文长度相当
3. 对于新闻标题，保持新闻标题的简洁性，不要扩充解释
4. 如果不确定某个词的含义，保持原文
5. 使用地道的中文表达，但不要过度诠释
6. 直接返回翻译结果，不要添加"以下是翻译内容"、"翻译如下"等任何说明文字
7. 不要在翻译开头或结尾添加任何额外的解释或说明"""
                    },
                    {
                        "role": "user",
                        "content": f"请直接翻译：\n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translated_text = response.choices[0].message.content.strip()
            return translated_text
            
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            return text
            
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
