import time
from functools import lru_cache
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import httpx

class TranslatorService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = httpx.Client(timeout=120.0)  # 增加超时时间到120秒
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def batch_translate(self, texts, chunk_size=5):
        """
        批量翻译文本，每次处理chunk_size个文本
        """
        if not texts:
            return []
            
        results = []
        # 将文本分成小块处理，避免单次请求过大
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i + chunk_size]
            try:
                translated_chunk = self._translate_chunk(chunk)
                
                # 打印翻译结果
                logging.info(f"\n翻译结果 (Chunk {i//chunk_size + 1}):")
                for idx, (original, translated) in enumerate(zip(chunk, translated_chunk), 1):
                    logging.info(f"\n原文 {idx}:\n{original}")
                    logging.info(f"译文 {idx}:\n{translated}")
                    logging.info(f"{'-'*30}")
                
                results.extend(translated_chunk)
                # 添加短暂延迟避免API限制
                time.sleep(1)
            except Exception as e:
                logging.error(f"Translation error for chunk {i}: {str(e)}")
                # 如果某个块失败，使用原文
                results.extend(chunk)
                
        return results
        
    def _translate_chunk(self, texts):
        """处理单个文本块的翻译"""
        messages = [
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": f"Translate the following English text to Chinese. Keep HTML tags unchanged: {json.dumps(texts)}"}
        ]
        
        response = self.client.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.3
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result['choices'][0]['message']['content']
            try:
                # 解析返回的JSON字符串
                return json.loads(translated_text)
            except:
                # 如果解析失败，尝试简单分割
                return translated_text.split('\n')
        else:
            raise Exception(f"Translation API error: {response.status_code}")
