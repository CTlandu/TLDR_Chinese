import requests
from functools import lru_cache
import time
import logging

class TranslatorService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"  # DeepSeek API 端点
        
    @lru_cache(maxsize=128)
    def translate_to_chinese(self, text, timestamp=None):
        if timestamp is None:
            timestamp = time.strftime('%Y%m%d')
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat-v3",  # 使用 DeepSeek v3 模型
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的翻译专家，请将以下英文内容翻译成地道的中文。保持专业性，同时确保翻译后的内容通俗易懂。"
                    },
                    {
                        "role": "user",
                        "content": f"请翻译以下内容：\n\n{text}"
                    }
                ],
                "temperature": 0.3,  # 降低随机性，保持翻译的稳定性
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                return translated_text
            else:
                logging.error(f"Translation API error: {response.status_code} - {response.text}")
                return text
                
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            return text
