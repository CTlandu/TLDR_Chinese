from flask import current_app
from api.services.mailgun_service import MailgunService
from api.models.subscriber import Subscriber
from api.models.article import DailyNewsletter
from datetime import datetime
import logging

def generate_newsletter_html(newsletter) -> str:
    """生成邮件的 HTML 内容"""
    # 获取当天日期的格式化字符串，用于生成链接
    newsletter_date = newsletter.date.strftime('%Y-%m-%d')
    
    html = f"""
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; font-size: 24px; margin: 0; padding: 20px 0; border-bottom: 2px solid #eee;">
                TLDR Chinese 每日科技新闻
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