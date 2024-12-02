import requests
from flask import current_app
import logging
from typing import Optional
import json
from api.models.subscriber import Subscriber

class MailgunService:
    def __init__(self, api_key: str, domain: str):
        self.api_key = api_key
        self.domain = domain
        self.base_url = f"https://api.mailgun.net/v3/{domain}"
        
    def send_confirmation_email(self, to_email: str, confirmation_link: str) -> dict:
        """发送订阅确认邮件"""
        try:
            return requests.post(
                f"{self.base_url}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"【太长不看】科技日推 <confirm@{self.domain}>",
                    "to": [to_email],
                    "subject": "确认订阅 【太长不看】 科技日推",
                    "html": self._get_confirmation_template(confirmation_link)
                }
            )
        except Exception as e:
            logging.error(f"Failed to send confirmation email: {str(e)}")
            raise
            
    def send_daily_newsletter(self, subscribers: list, subject: str, content: str) -> dict:
        """发送每日新闻邮件"""
        try:
            # 为每个收件人准备变量
            recipient_vars = {
                email: {
                    'id': str(Subscriber.objects(email=email).first().id)
                } for email in subscribers
            }
            
            return requests.post(
                f"{self.base_url}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"【太长不看】科技日推 <newsletter@{self.domain}>",
                    "to": subscribers,
                    "subject": subject,
                    "html": content,
                    "recipient-variables": json.dumps(recipient_vars),  # 添加收件人变量
                    "h:Reply-To": f"support@{self.domain}",
                    "o:tag": ["daily-newsletter"],
                    "o:dkim": "yes",
                    "o:tracking": "yes",
                    "o:tracking-clicks": "yes",
                    "o:tracking-opens": "yes",
                    "o:require-tls": "yes",
                    "o:skip-verification": "no"
                }
            )
        except Exception as e:
            logging.error(f"Failed to send newsletter: {str(e)}")
            raise
            
    def _get_confirmation_template(self, confirmation_link: str) -> str:
        """确认邮件的 HTML 模板"""
        return f"""
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>确认订阅 【太长不看】 科技日推</h2>
            <p>感谢您订阅 【太长不看】 每日科技新闻！</p>
            <p>请点击下面的按钮确认您的订阅：</p>
            <p style="text-align: center;">
                <a href="{confirmation_link}" 
                   style="display: inline-block; padding: 12px 24px; 
                          background-color: #0066cc; color: white; 
                          text-decoration: none; border-radius: 4px;">
                    确认订阅
                </a>
            </p>
            <p>如果按钮无法点击，请复制以下链接到浏览器中打开：</p>
            <p>{confirmation_link}</p>
        </div>
        """
            
    def send_simple_message(self, to_email: str, subject: str, text: str) -> dict:
        """发送简单的测试邮件"""
        try:
            # 打印请求信息用于调试
            logging.info(f"Sending email to: {to_email}")
            logging.info(f"Using domain: {self.domain}")
            
            response = requests.post(
                f"{self.base_url}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"TLDR Chinese <mailgun@{self.domain}>",
                    "to": [to_email],
                    "subject": subject,
                    "text": text
                }
            )
            
            # 打印响应信息
            logging.info(f"Status code: {response.status_code}")
            logging.info(f"Response text: {response.text}")
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 尝试解析 JSON 响应
            try:
                return response.json()
            except ValueError:
                # 如果响应不是 JSON 格式，返回原始响应文本
                return {"message": response.text}
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise
        
    def generate_newsletter_html(self, newsletter) -> str:
        """生成邮件的 HTML 内容"""
        newsletter_date = newsletter.date.strftime('%Y-%m-%d')
        
        html = f"""
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2c3e50; font-size: 24px; margin: 0; padding: 20px 0; border-bottom: 2px solid #eee;">
                    【太长不看】科技日推
                </h1>
                <p style="color: #7f8c8d; margin-top: 10px;">
                    {newsletter_date}
                </p>
                <p style="color: #666; margin-top: 20px; font-size: 14px; line-height: 1.6;">
                    若想获得更好阅读体验以及中英双语内容，请访问：
                    <a href="https://www.tldrnewsletter.cn/newsletter/{newsletter_date}" 
                    style="color: #3498db; text-decoration: none; font-weight: 500;"
                    target="_blank">
                        www.tldrnewsletter.cn/newsletter/{newsletter_date}
                    </a>
                </p>
            </div>
            
            <div style="margin-top: 30px;">
        """
        
        # 遍历所有分类的新闻（不再跳过任何板块）
        for section in newsletter.sections:
            html += f"""
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #2c3e50; font-size: 20px; margin: 0 0 20px 0; 
                            padding-bottom: 10px; border-bottom: 2px solid #eee;">
                        {section['section']}
                    </h2>
            """
            
            # 遍历该分类下的所有文章
            for article in section['articles']:
                image_html = ""
                if article.get('image_url'):
                    image_html = f"""
                        <div style="text-align: center; margin: 15px 0;">
                            <img src="{article['image_url']}" 
                                style="max-width: 100%; height: 150px; object-fit: cover; 
                                        border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                                alt="{article['title']}"
                            />
                        </div>
                    """
                    
                html += f"""
                    <div style="background: #fff; border-radius: 8px; margin-bottom: 25px; 
                            padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        {image_html}
                        <h3 style="color: #2c3e50; font-size: 18px; margin: 0 0 15px 0; line-height: 1.4;">
                            {article['title']}
                        </h3>
                        <p style="color: #34495e; line-height: 1.6; margin: 0 0 15px 0; font-size: 16px;">
                            {article['content']}
                        </p>
                        <div style="text-align: right;">
                            <a href="{article['url']}" 
                            style="display: inline-block; color: #3498db; text-decoration: none; 
                                    font-weight: 500; font-size: 14px;"
                            target="_blank">
                                阅读原文 →
                            </a>
                        </div>
                    </div>
                """
                
            html += "</div>"
        
        # 获取后端 URL
        backend_url = current_app.config['BACKEND_URL'].rstrip('/')
        
        # 添加页脚（包含版权信息）
        html += f"""
            </div>
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; 
                        text-align: center; color: #7f8c8d;">
                <p style="margin: 0 0 10px 0; font-size: 14px;">
                    感谢订阅 TLDR Chinese！
                </p>
                <p style="margin: 0 0 10px 0; font-size: 12px; color: #95a5a6;">
                    版权来自于 TLDR TECH NEWS @ 
                    <a href="https://tldr.tech/" 
                    style="color: #3498db; text-decoration: none;"
                    target="_blank">
                        https://tldr.tech/
                    </a>
                </p>
                <p style="margin: 10px 0; font-size: 12px;">
                    <a href="{backend_url}/api/unsubscribe/%recipient.id%" 
                    style="color: #3498db; text-decoration: none;">
                        取消订阅
                    </a>
                </p>
            </div>
        </div>
        """
        
        return html
