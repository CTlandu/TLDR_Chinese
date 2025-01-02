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
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的翻译专家，请将以下英文内容翻译成地道的中文。保持专业性，同时确保翻译后的内容通俗易懂。"
                    },
                    {
                        "role": "user",
                        "content": f"请翻译以下内容：\n\n{text}"
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
