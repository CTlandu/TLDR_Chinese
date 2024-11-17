from flask import current_app
from api.services.mailgun_service import MailgunService
from api.models.subscriber import Subscriber
from api.models.article import DailyNewsletter
from datetime import datetime
import logging

def generate_newsletter_html(newsletter) -> str:
    """生成邮件的 HTML 内容"""
    html = f"""
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h1 style="color: #333; text-align: center;">
            TLDR Chinese 每日科技新闻 【{newsletter.date.strftime('%Y-%m-%d')}】
        </h1>
        
        <div style="margin-top: 30px;">
    """
    
    # 遍历每个分类的新闻
    for section in newsletter.sections:
        html += f"""
            <h2 style="color: #0066cc; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                {section['section']}
            </h2>
        """
        
        # 遍历该分类下的所有文章
        for article in section['articles']:
            html += f"""
                <div style="margin-bottom: 25px;">
                    <h3 style="color: #444; margin-bottom: 10px;">
                        {article['title']}
                    </h3>
                    <p style="color: #666; line-height: 1.6;">
                        {article['content']}
                    </p>
                    <a href="{article['url']}" 
                       style="color: #0066cc; text-decoration: none;"
                       target="_blank">
                        阅读原文 →
                    </a>
                </div>
            """
    
    # 添加页脚
    html += """
        </div>
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666;">
            <p>
                感谢订阅 TLDR Chinese！
                <br>
                如果想要退订，请点击 <a href="%unsubscribe_url%" style="color: #0066cc;">这里</a>
            </p>
        </div>
    </div>
    """
    
    return html

def send_daily_newsletter():
    try:
        # 获取今日新闻
        today = datetime.utcnow().date()
        newsletter = DailyNewsletter.objects(date=today).first()
        
        if not newsletter:
            logging.warning(f"No newsletter found for {today}")
            return
            
        # 获取已确认的订阅者
        confirmed_subscribers = Subscriber.objects(confirmed=True).all()
        subscriber_emails = [s.email for s in confirmed_subscribers]
        
        if not subscriber_emails:
            logging.info("No confirmed subscribers")
            return
            
        # 准备邮件内容
        subject = f"TLDR Chinese 每日科技新闻 【{today.strftime('%Y-%m-%d')}】"
        content = generate_newsletter_html(newsletter)
        
        # 发送邮件
        mailgun = MailgunService(
            current_app.config['MAILGUN_API_KEY'],
            current_app.config['MAILGUN_DOMAIN']
        )
        
        result = mailgun.send_daily_newsletter(
            subscriber_emails,
            subject,
            content
        )
        
        logging.info(f"Newsletter sent to {len(subscriber_emails)} subscribers")
        return result
        
    except Exception as e:
        logging.error(f"Failed to send newsletter: {str(e)}")
        raise