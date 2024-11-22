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
                    "from": f"TLDR每日科技新闻 <TLDR科技日推@{self.domain}>",
                    "to": [to_email],
                    "subject": "确认订阅 TLDR 科技日推",
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
                    "from": f"TLDR Chinese <newsletter@{self.domain}>",
                    "to": subscribers,
                    "subject": subject,
                    "html": content,
                    "recipient-variables": json.dumps(recipient_vars),  # 添加收件人变量
                    "h:Reply-To": f"support@{self.domain}",
                    "o:tag": ["daily-newsletter"],
                    "o:dkim": "yes",
                    "o:tracking": "yes",
                    "o:tracking-clicks": "yes",
                    "o:tracking-opens": "yes"
                }
            )
        except Exception as e:
            logging.error(f"Failed to send newsletter: {str(e)}")
            raise
            
    def _get_confirmation_template(self, confirmation_link: str) -> str:
        """确认邮件的 HTML 模板"""
        return f"""
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>确认订阅 TLDR 科技日推</h2>
            <p>感谢您订阅 TLDR 每日科技新闻！</p>
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