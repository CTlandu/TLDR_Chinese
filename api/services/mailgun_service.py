import requests
from flask import current_app
import logging

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
                    "from": f"TLDR Chinese <mailgun@{self.domain}>",
                    "to": [to_email],
                    "subject": "确认订阅 TLDR Chinese 每日科技新闻",
                    "html": self._get_confirmation_template(confirmation_link)
                }
            )
        except Exception as e:
            logging.error(f"Failed to send confirmation email: {str(e)}")
            raise
            
    def send_daily_newsletter(self, subscribers: list, subject: str, content: str) -> dict:
        """发送每日新闻邮件"""
        try:
            return requests.post(
                f"{self.base_url}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"TLDR Chinese <mailgun@{self.domain}>",
                    "to": subscribers,
                    "subject": subject,
                    "html": content,
                    "tracking-opens": "yes",
                    "tracking-clicks": "yes"
                }
            )
        except Exception as e:
            logging.error(f"Failed to send newsletter: {str(e)}")
            raise
            
    def _get_confirmation_template(self, confirmation_link: str) -> str:
        """确认邮件的 HTML 模板"""
        return f"""
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>确认订阅 TLDR Chinese</h2>
            <p>感谢您订阅 TLDR Chinese 每日科技新闻！</p>
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
            return requests.post(
                f"{self.base_url}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"TLDR Chinese <mailgun@{self.domain}>",
                    "to": [to_email],
                    "subject": subject,
                    "text": text
                }
            ).json()
        except Exception as e:
            logging.error(f"Failed to send test email: {str(e)}")
            raise