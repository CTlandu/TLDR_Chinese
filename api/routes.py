from flask import Blueprint, jsonify, request, url_for, current_app, redirect
from .services.newsletter import get_newsletter, fetch_tldr_content
from datetime import datetime
import pytz
from datetime import timedelta
from .services.emoji_mapper import get_section_emoji, clean_reading_time, get_title_emoji
from .models.article import DailyNewsletter
import logging
from flask import make_response
from .services.mailgun_service import MailgunService
from .models.subscriber import Subscriber
import secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
from disposable_email_domains import blocklist

bp = Blueprint('main', __name__)

#######################
# CORS Configuration #
#######################

@bp.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed_origins = [
        'https://www.tldrnewsletter.cn',
        'http://localhost:5173',  # 添加本地开发环境
        'http://localhost:3000',
        'https://tldrnewsletter.cn',
        'https://tldr-chinese-frontend.onrender.com',
        'https://tldr-chinese-backend.onrender.com',
        # 如果你使用其他端口也可以添加
    ]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'false')
    return response

########################
# Helper Functions     #
########################

def get_available_dates(days=7):
    et = pytz.timezone('US/Eastern')
    dates = []
    current = datetime.now(et)
    
    for i in range(days):
        date = current - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    return dates

########################
# Core Website Routes  #
########################

@bp.route('/api/newsletter/<date>')
def get_newsletter_by_date(date):
    try:
        articles = get_newsletter(date)
        
        if not articles:
            return jsonify({
                'articles': [],
                'currentDate': date,
                'dates': get_available_dates()
            }), 200
            
        # 获取实际返回的文章日期
        actual_date = date
        if DailyNewsletter.objects(sections=articles).first():
            actual_date = DailyNewsletter.objects(sections=articles).first().date.strftime('%Y-%m-%d')
            
        processed_articles = []
        for section in articles:
            if not isinstance(section, dict) or 'section' not in section:
                continue
                
            processed_section = {
                'section': get_section_emoji(section['section']),
                'articles': []
            }
            
            if 'articles' in section and isinstance(section['articles'], list):
                for article in section['articles']:
                    if isinstance(article, dict):
                        processed_article = article.copy()
                        if 'title' in processed_article:
                            processed_article['title'] = get_title_emoji(article['title'])
                        processed_section['articles'].append(processed_article)
            
            processed_articles.append(processed_section)
        
        return jsonify({
            'articles': processed_articles,
            'currentDate': actual_date,  # 返回实际的日期
            'dates': get_available_dates()
        })
            
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': '暂时无法获取新闻内容，请稍后再试',
            'articles': [],
            'currentDate': date,
            'dates': get_available_dates()
        }), 200

@bp.route('/api/latest-articles')
def get_latest_articles():
    try:
        # 获取当前时间（美东时间）
        et = pytz.timezone('US/Eastern')
        current_date = datetime.now(et)
        logging.info(f"Current ET date: {current_date}")

        # 获取所有可用的newsletter，按日期降序排列
        all_newsletters = DailyNewsletter.objects().order_by('-date')
        logging.info(f"Total newsletters in database: {all_newsletters.count()}")
        
        # 获取最新的newsletter
        latest_newsletter = all_newsletters.first()
        if not latest_newsletter:
            logging.warning("No newsletters found in database")
            return jsonify([])
        
        latest_date = latest_newsletter.date.strftime('%Y-%m-%d')
        logging.info(f"Latest newsletter date: {latest_date}")
        
        # 检查是否有更新的内容
        today_date = current_date.strftime('%Y-%m-%d')
        if latest_date != today_date:
            logging.info(f"Checking for newer content for {today_date}")
            # 尝试获取今天的内容
            today_articles = fetch_tldr_content(today_date)
            if today_articles:
                logging.info("Found newer content, using it instead")
                # 如果找到了今天的内容，保存并使用它
                try:
                    new_newsletter = DailyNewsletter(
                        date=current_date,
                        sections=today_articles
                    )
                    new_newsletter.save()
                    latest_newsletter = new_newsletter
                    latest_date = today_date
                except Exception as e:
                    logging.error(f"Error saving new newsletter: {str(e)}")
        
        # 处理文章数据
        flattened_articles = []
        for section in latest_newsletter.sections:
            processed_section = get_section_emoji(section['section'])
            logging.info(f"Processing section: {section['section']}")
            
            for article in section['articles']:
                processed_article = {
                    'title': get_title_emoji(clean_reading_time(article['title'])),
                    'title_en': clean_reading_time(article['title_en']),
                    'content': article['content'],
                    'content_en': article['content_en'],
                    'url': article['url'],
                    'image_url': article.get('image_url'),
                    'section': processed_section,
                    'date': latest_date
                }
                flattened_articles.append(processed_article)
        
        logging.info(f"Returning {len(flattened_articles)} articles for date {latest_date}")
        return jsonify(flattened_articles)
        
    except Exception as e:
        logging.error(f"Error in get_latest_articles: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/latest-articles-by-section')
def get_latest_articles_by_section():
    try:
        # 获取所有newsletter，按日期降序排列
        all_newsletters = DailyNewsletter.objects().order_by('-date')
        
        # 定义我们想要的分区
        sections_to_show = {
            'Big Tech & Startups': [],
            'Science & Futuristic Technology': [],
            'Programming, Design & Data Science': [],
            'Miscellaneous': [],
            'Quick Links': []
        }
        
        # 获取当前时间用于计算相对时间
        now = datetime.now(pytz.timezone('US/Eastern'))
        
        # 遍历所有newsletter
        for newsletter in all_newsletters:
            newsletter_date = newsletter.date
            days_ago = (now.date() - newsletter_date).days
            
            # 格式化相对时间
            if days_ago == 0:
                relative_time = "今天"
            elif days_ago == 1:
                relative_time = "昨天"
            else:
                relative_time = f"{days_ago}天前"
            
            # 处理每个分区
            for section in newsletter.sections:
                section_name = section['section']
                if section_name in sections_to_show and len(sections_to_show[section_name]) < 5:
                    # 处理该分区的文章
                    for article in section['articles']:
                        if article.get('image_url') and len(sections_to_show[section_name]) < 5:
                            processed_article = {
                                'title': get_title_emoji(clean_reading_time(article['title'])),
                                'content': article['content'],
                                'url': article['url'],
                                'image_url': article['image_url'],
                                'relative_time': relative_time
                            }
                            sections_to_show[section_name].append(processed_article)
        
        return jsonify(sections_to_show)
        
    except Exception as e:
        logging.error(f"Error in get_latest_articles_by_section: {str(e)}")
        return jsonify({'error': str(e)}), 500

########################
# WeChat Integration   #
########################

@bp.route('/api/wechat/newsletter/<date>')
def get_wechat_newsletter(date):
    try:
        # 转换为美东时间
        et = pytz.timezone('US/Eastern')
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_et = et.localize(date_obj)
        
        # 使用美东时间的日期获取新闻
        articles = get_newsletter(date_et.strftime('%Y-%m-%d'))
        
        if not articles:
            logging.warning(f"No content available for date: {date} ET")
            return jsonify({
                'error': f'未找到 {date} (美东时间) 的新闻内容，可能是无效日期或内容尚未发布',
                'articles': [],
                'currentDate': date
            }), 404
        
        # 需要排除的板
        excluded_sections = ['Programming, Design & Data Science', 'Quick Links']
        
        # 创建扁平化的文章列表
        flattened_articles = []
        
        for section in articles:
            # 跳过不需要的板块
            if section['section'] in excluded_sections:
                continue
                
            section_name = get_section_emoji(section['section'])
            
            for article in section['articles']:
                # 清理中英文标题中的阅读时间
                title_zh = clean_reading_time(article['title'])
                title_en = clean_reading_time(article['title_en'])
                
                # 添加表情符号
                title_zh = get_title_emoji(title_zh)
                
                processed_article = {
                    'title': title_zh,
                    'title_en': title_en,
                    'content': article['content'],
                    'content_en': article['content_en'],
                    'url': article.get('url', ''),
                    'section': section_name
                }
                flattened_articles.append(processed_article)
        
        return jsonify({
            'articles': flattened_articles,
            'currentDate': date
        })
        
    except Exception as e:
        logging.error(f"Error in get_wechat_newsletter: {str(e)}")
        return jsonify({
            'error': '获取新闻内容时发生错误，请稍后重试',
            'articles': [],
            'currentDate': date
        }), 500

########################
# Subscription Routes  #
########################

# 创建限流器
limiter = Limiter(
    app=None,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # 使用内存存储，也可以配置 redis
)

# 一次性邮箱域名检查函数
def is_disposable_email(email):
    try:
        domain = email.split('@')[1].lower()
        return domain in blocklist
    except:
        return True

# 邮箱格式验证函数
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    # 检查域名部分是否包含至少一个点号
    domain = email.split('@')[1]
    return '.' in domain

@bp.route('/api/subscribe', methods=['POST'])
@limiter.limit("5 per hour")  # 每小时限制5次订阅请求
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        # 基本验证
        if not email:
            return jsonify({'error': '请提供邮箱地址'}), 400
            
        # 格式验证
        if not is_valid_email(email):
            return jsonify({'error': '无效的邮箱格式'}), 400
            
        # 一次性邮箱检查
        if is_disposable_email(email):
            return jsonify({'error': '不支持一次性邮箱地址'}), 400
            
        # 检查邮箱是否已存在
        existing_subscriber = Subscriber.objects(email=email).first()
        
        if existing_subscriber:
            if existing_subscriber.confirmed:
                return jsonify({'error': '该邮箱已订阅'}), 400
            else:
                # 重新发送确认邮件的逻辑...
                confirmation_link = url_for(
                    'main.confirm_subscription',
                    token=existing_subscriber.confirmation_token,
                    _external=True
                )
                
                mailgun = MailgunService(
                    current_app.config['MAILGUN_API_KEY'],
                    current_app.config['MAILGUN_DOMAIN']
                )
                
                mailgun.send_confirmation_email(email, confirmation_link)
                return jsonify({'message': '确认邮件已重新发送，请查收'})
        
        # 创建新订阅者
        confirmation_token = secrets.token_urlsafe(32)
        subscriber = Subscriber(
            email=email,
            confirmation_token=confirmation_token
        )
        subscriber.save()
        
        # 发送确认邮件...
        confirmation_link = url_for(
            'main.confirm_subscription',
            token=confirmation_token,
            _external=True
        )
        
        mailgun = MailgunService(
            current_app.config['MAILGUN_API_KEY'],
            current_app.config['MAILGUN_DOMAIN']
        )
        
        mailgun.send_confirmation_email(email, confirmation_link)
        
        return jsonify({
            'message': '确认邮件已发送，请查收并点击确认链接完成订阅'
        })
        
    except Exception as e:
        logging.error(f"Subscription error: {str(e)}")
        return jsonify({'error': '订阅失败，请稍后重试'}), 500
    
    
@bp.route('/api/confirm/<token>', methods=['GET'])
def confirm_subscription(token):
    try:
        subscriber = Subscriber.objects(confirmation_token=token).first()
        frontend_url = current_app.config['FRONTEND_URL']
        
        # 添加日志
        logging.info(f"Confirming subscription with token: {token}")
        logging.info(f"Frontend URL: {frontend_url}")
        
        if not subscriber:
            redirect_url = f"{frontend_url}/subscription/error?message=invalid_token"
            logging.info(f"Redirecting to: {redirect_url}")
            return redirect(redirect_url)
            
        if subscriber.confirmed:
            redirect_url = f"{frontend_url}/subscription/success?status=already_confirmed"
            logging.info(f"Redirecting to: {redirect_url}")
            return redirect(redirect_url)
            
        subscriber.confirm_subscription()
        
        redirect_url = f"{frontend_url}/subscription/success?verified=true&token={token}"
        logging.info(f"Redirecting to: {redirect_url}")
        return redirect(redirect_url)
        
    except Exception as e:
        logging.error(f"Confirmation error: {str(e)}")
        return redirect(f"{frontend_url}/subscription/error")
    
    
@bp.route('/api/unsubscribe/<subscriber_id>',methods=['GET'])
def unsubscribe(subscriber_id):
    try:
        # 查找并更新订阅者状态
        subscriber = Subscriber.objects(id=subscriber_id).first()
        
        if not subscriber:
            return jsonify({'error': '未找到订阅者'}), 404
            
        # 如果已经取消订阅，直接重定向
        if not subscriber.confirmed:
            return redirect(f"{current_app.config['FRONTEND_URL']}/unsubscribed")
            
        # 删除订阅者
        subscriber.delete()
        
        # 重定向到前端的取消订阅成功页面
        return redirect(f"{current_app.config['FRONTEND_URL']}/unsubscribed")
        
    except Exception as e:
        logging.error(f"Unsubscribe error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    
########################
# Email Service Routes #
########################

@bp.route('/api/test/send_newsletter', methods=['POST'])
def test_send_newsletter():
    try:
        latest_newsletter = DailyNewsletter.objects.order_by('-date').first()
        
        if not latest_newsletter:
            return jsonify({'error': '没有找到可用的 newsletter'}), 404
            
        subject = f"TLDR 全球科技日报 {latest_newsletter.date.strftime('%Y-%m-%d')}"
        
        # 创建 Mailgun 服务实例
        mailgun = MailgunService(
            current_app.config['MAILGUN_API_KEY'],
            current_app.config['MAILGUN_DOMAIN']
        )
        
        # 使用 mailgun 实例生成 HTML
        html_content = mailgun.generate_newsletter_html(latest_newsletter)
        
        test_email = "jizhoutang@outlook.com"
        response = mailgun.send_daily_newsletter(
            [test_email],
            subject,
            html_content
        )
        
        return jsonify({
            'message': f'测试邮件已发送至 {test_email}',
            'status_code': response.status_code,
            'response_text': response.text
        })
        
    except Exception as e:
        logging.error(f"Failed to send test newsletter: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    
@bp.route('/api/send_daily_newsletter', methods=['POST'])
def send_daily_newsletter_api():
    try:
        # 验证请求（可以添加 API key 验证）
        api_key = request.headers.get('X-API-Key')
        if api_key != current_app.config.get('NEWSLETTER_API_KEY'):
            return jsonify({'error': '未授权的请求'}), 401
            
        # 获取最新的 newsletter
        latest_newsletter = DailyNewsletter.objects.order_by('-date').first()
        
        if not latest_newsletter:
            return jsonify({'error': '没有找到可用的 newsletter'}), 404
            
        # 获取所有已确认的订阅者
        confirmed_subscribers = Subscriber.objects(confirmed=True).all()
        subscriber_emails = [s.email for s in confirmed_subscribers]
        
        if not subscriber_emails:
            return jsonify({'message': '没有已确认的订阅者'}), 200
            
        # 准备邮件内容
        subject = f"TLDR Chinese 每日科技新闻 【{latest_newsletter.date.strftime('%Y-%m-%d')}】"
        
        # 创建 Mailgun 服务实例
        mailgun = MailgunService(
            current_app.config['MAILGUN_API_KEY'],
            current_app.config['MAILGUN_DOMAIN']
        )
        
        # 使用 mailgun 实例生成 HTML
        html_content = mailgun.generate_newsletter_html(latest_newsletter)
        
        response = mailgun.send_daily_newsletter(
            subscriber_emails,
            subject,
            html_content
        )
        
        return jsonify({
            'message': f'成功发送每日新闻给 {len(subscriber_emails)} 位订阅者',
            'date': latest_newsletter.date.strftime('%Y-%m-%d'),
            'subscriber_count': len(subscriber_emails),
            'status_code': response.status_code,
            'response_text': response.text
        })
        
    except Exception as e:
        logging.error(f"Failed to send daily newsletter: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
########################
# Miscellaneous Routes #
@bp.route('/api/subscriber-count', methods=['GET'])
def get_subscriber_count():
    try:
        # 获取已确认的订阅者数量
        confirmed_subscribers_count = Subscriber.objects(confirmed=True).count()
        base_count = 4738  # 基础数量
        total_count = base_count + confirmed_subscribers_count
        
        return jsonify({
            'count': total_count,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"Error getting subscriber count: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500
    
    
    
