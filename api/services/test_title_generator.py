import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api import create_app
from api.models.article import DailyNewsletter
from api.services.title_generator import TitleGeneratorService
import json
from datetime import datetime
import pytz

def test_title_generation():
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        # 从应用配置中获取API key
        api_key = app.config['GEMINI_API_KEY']
        if not api_key:
            print("未在配置中找到 GEMINI_API_KEY")
            return

        # 初始化服务
        title_generator = TitleGeneratorService(api_key)
        
        # 获取最近的几期newsletter进行测试
        newsletters = DailyNewsletter.objects.order_by('-date')[:3]
        
        print("\n=== 开始测试标题生成 ===\n")
        
        for newsletter in newsletters:
            date = newsletter.date.strftime('%Y-%m-%d')
            print(f"\n日期: {date}")
            print("原文标题:")
            for section in newsletter.sections[:2]:  # 只打印前两个板块作为参考
                for article in section['articles'][:2]:
                    print(f"- {article['title']}")
            
            # 生成新标题
            title = title_generator.generate_title(newsletter.sections)
            print(f"\n生成的标题: {title}")
            print(f"标题长度: {len(title)} 字符")
            print("\n" + "="*50)

if __name__ == "__main__":
    test_title_generation()