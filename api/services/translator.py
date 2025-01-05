import time
from functools import lru_cache
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import httpx
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

class TranslatorService:
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        # 创建一个持久的 session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    @retry(stop=stop_after_attempt(3), 
           wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_access_token(self) -> str:
        """获取百度智能云 access token"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = self.session.post(url, params=params)
            result = response.json()
            if 'access_token' in result:
                return result['access_token']
            raise Exception(f"获取 access token 失败: {result}")
        except Exception as e:
            logging.error(f"获取 access token 出错: {str(e)}")
            raise
            
    @retry(stop=stop_after_attempt(3), 
           wait=wait_exponential(multiplier=1, min=4, max=10))
    def batch_translate(self, texts, chunk_size=3):
        """批量翻译文本"""
        if not texts:
            return []
            
        results = []
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i + chunk_size]
            try:
                # 打印待翻译内容
                logging.info(f"\n{'='*50}\n待翻译内容 (Chunk {i//chunk_size + 1}):")
                for idx, text in enumerate(chunk, 1):
                    logging.info(f"\n原文 {idx}:\n{text}")
                
                translated_chunk = self._translate_chunk(chunk)
                results.extend(translated_chunk)
                
                # 打印翻译结果
                logging.info(f"\n翻译结果 (Chunk {i//chunk_size + 1}):")
                for idx, (original, translated) in enumerate(zip(chunk, translated_chunk), 1):
                    logging.info(f"\n原文 {idx}:\n{original}")
                    logging.info(f"译文 {idx}:\n{translated}")
                    logging.info(f"{'-'*30}")
                
                # 添加短暂延迟避免API限制
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Translation error for chunk {i}: {str(e)}")
                # 如果翻译失败，使用原文
                results.extend(chunk)
                
        return results
        
    def _translate_chunk(self, texts):
        """处理单个文本块的翻译"""
        if not self.access_token:
            self.access_token = self._get_access_token()
            
        combined_text = "\n===SPLIT===\n".join(texts)
        logging.info(f"准备翻译的文本:\n{combined_text}")
        
        try:
            response = self.session.post(
                "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
                headers={
                    "Content-Type": "application/json"
                },
                params={"access_token": self.access_token},
                json={
                    "messages": [{
                        "role": "user", 
                        "content": f"You are a professional translator. Please translate the following English text to Chinese. Keep the original format and DO NOT add any HTML tags:\n\n{combined_text}"
                    }],
                    "temperature": 0.3
                },
                timeout=30
            )
            
            logging.info(f"API 响应状态码: {response.status_code}")
            logging.info(f"API 响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    translations = result['result'].split("\n===SPLIT===\n")
                    logging.info(f"翻译结果:\n{translations}")
                    if len(translations) != len(texts):
                        logging.error(f"翻译数量不匹配: 输入 {len(texts)} 段，输出 {len(translations)} 段")
                    return translations
                    
            raise Exception(f"Translation API error: {response.json()}")
            
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            raise
