import deepl
from functools import lru_cache
import time

class TranslatorService:
    def __init__(self, api_key):
        self.translator = deepl.Translator(api_key)
    
    @lru_cache(maxsize=128)
    def translate_to_chinese(self, text, timestamp=None):
        if timestamp is None:
            timestamp = time.strftime('%Y%m%d')
        try:
            result = self.translator.translate_text(
                text,
                target_lang="ZH",
                tag_handling="html",
                formality="default"
            )
            return str(result)
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return text
