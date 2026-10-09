from flask import Blueprint, jsonify, request, url_for, current_app, redirect
from .services.newsletter import get_newsletter, fetch_tldr_content
from datetime import datetime
import pytz
from datetime import timedelta
from .services.emoji_mapper import get_section_emoji, clean_reading_time, get_title_emoji
from .models.article import DailyNewsletter
import logging
from flask import make_response
from .services.resend_client import ResendClient
from .services.newsletter_email import (
    UNSUBSCRIBE_TOKEN_PLACEHOLDER,
    confirmation_email_html,
    generate_newsletter_html,
)
from .services.subscriber_sync import run_sync
from .services.unsubscribe_feedback import clean_comment, clean_reasons
from .models.subscriber import Subscriber
from bson import ObjectId
import secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
import disposable_email_domains
import requests
import json
from io import BytesIO
import base64
from .services.title_generator import TitleGeneratorService

bp = Blueprint('main', __name__)

#######################
# CORS Configuration #
#######################

@bp.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    
    # 动态允许的域名模式
    allowed_patterns = [
        'localhost',
        'vercel.app',  # 允许所有 Vercel 域名（包括预览部署）
        'tldrnewsletter.cn',
        'onrender.com'
    ]
    
    # 检查 origin 是否匹配允许的模式
    if origin:
        for pattern in allowed_patterns:
            if pattern in origin:
                response.headers.add('Access-Control-Allow-Origin', origin)
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
                response.headers.add('Access-Control-Allow-Credentials', 'false')
                break
    
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
        # 先查询指定日期
        newsletter = DailyNewsletter.objects(date=date).first()
        if newsletter:
            response_data = {
                'currentDate': newsletter.date.strftime('%Y-%m-%d'),
                'sections': newsletter.sections,
                'generated_title': newsletter.generated_title
            }
            resp = jsonify(response_data)
            resp.headers['Cache-Control'] = 'public, max-age=3600, stale-while-revalidate=86400'
            return resp
            
        # 如果数据库中没有，尝试获取并保存
        articles = get_newsletter(date)
        
        # 再次检查数据库，因为 get_newsletter 可能已经保存了数据
        newsletter = DailyNewsletter.objects(date=date).first()
        if newsletter:
            return jsonify({
                'currentDate': newsletter.date.strftime('%Y-%m-%d'),
                'sections': newsletter.sections,
                'generated_title': newsletter.generated_title
            })
            
        # 如果还是没有找到，使用 articles 的数据
        if articles and isinstance(articles, dict) and 'sections' in articles:
            return jsonify({
                'currentDate': articles.get('date', date),
                'sections': articles['sections'],
                'generated_title': articles['generated_title']
            })
            
        # 如果还是找不到，返回最新的 newsletter
        latest_newsletter = DailyNewsletter.objects().order_by('-date').first()
        if latest_newsletter:
            return jsonify({
                'currentDate': latest_newsletter.date.strftime('%Y-%m-%d'),
                'sections': latest_newsletter.sections,
                'generated_title': latest_newsletter.generated_title
            })
            
        return jsonify({'error': 'No newsletter available'}), 404
        
    except Exception as e:
        logging.error(f"Error getting newsletter: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/latest-articles')
def get_latest_articles():
    try:
        # 获取数据库中最新的 newsletter 日期
        latest_newsletter = DailyNewsletter.objects().order_by('-date').first()
        
        if not latest_newsletter:
            return jsonify({'error': '没有找到可用的 newsletter'}), 404
            
        # 使用最新日期调用 get_newsletter_by_date
        latest_date = latest_newsletter.date.strftime('%Y-%m-%d')
        return get_newsletter_by_date(latest_date)
        
    except Exception as e:
        logging.error(f"Error getting latest articles: {str(e)}")
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
                                'title': clean_reading_time(article['title']),
                                'title_en': article.get('title_en', ''),
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
                'currentDate': date,
                'generated_title': "错误，没找到title"
            }), 404
        
        # 获取 sections 和 generated_title
        sections = articles.get('sections', [])
        generated_title = articles.get('generated_title', '今日新闻')
        
        # 需要排除的板块
        excluded_sections = ['Programming, Design & Data Science', 'Quick Links']
        
        # 创建扁平化的文章列表和 HTML 字符串
        flattened_articles = []
        articles_html = []
        first_image_url = None  # 存储第一张图片的URL
        
        # 寻找第一张图片URL
        for section in sections:
            if first_image_url:
                break
                
            if section['section'] in excluded_sections:
                continue
                
            for article in section['articles']:
                if article.get('image_url'):
                    first_image_url = article['image_url']
                    break
        
        # 处理文章内容
        for section in sections:
            if section['section'] in excluded_sections:
                continue
                
            section_name = get_section_emoji(section['section'])
            
            for article in section['articles']:
                # 处理单篇文章
                title_zh = clean_reading_time(article['title'])
                title_en = clean_reading_time(article['title_en'])
                title_zh = get_title_emoji(title_zh)
                
                processed_article = {
                    'title': title_zh,
                    'title_en': clean_reading_time(article['title_en']),
                    'content': article['content'],
                    'content_en': article['content_en'],
                    'url': article.get('url', ''),
                    'section': section_name,
                    'image_url': article.get('image_url', '')
                }
                flattened_articles.append(processed_article)
                
                # 创建 HTML 格式的文章
                
                # 包含中英文
                # article_html = f'''<div style="margin-bottom:35px;"><p style="font-size:16px;font-weight:bold;color:#273469;margin-bottom:5px;text-decoration:underline;">{title_zh}</p><p style="font-size:15px;color:#30343f;margin-bottom:15px;font-style:italic;">{title_en}</p><p style="font-size:15px;color:#1e2749;line-height:1.6;margin-bottom:8px;">{article['content']}</p><div style="background-color:#f8f8f8;padding:10px;margin-bottom:12px;"><p style="font-size:12px;color:#666;line-height:1.6;font-style:italic;">{article['content_en']}</p></div><p style="font-size:10px;color:#1e88e5;margin-bottom:20px;">{article.get('url', '')}</p></div>'''

                # 只包含中文
                article_html = f'''<div style="margin-bottom:35px;"><p style="font-size:18px;font-weight:bold;color:#c0392b;margin-bottom:5px;">{title_zh}</p><p style="font-size:15px;color:#1e2749;line-height:1.6;margin-bottom:8px;">{article['content']}</p></div>'''
                articles_html.append(article_html)
        
        # 将所有 HTML 文章组合成一个字符串
        articles_in_html = ''.join(articles_html)
        
        return jsonify({
            'articles': flattened_articles,
            'currentDate': date,
            'generated_title': generated_title,
            'articles_in_html': articles_in_html,
            'first_image_url': first_image_url  # 返回第一张图片的URL
        })
        
    except Exception as e:
        logging.error(f"Error in get_wechat_newsletter: {str(e)}")
        return jsonify({
            'error': '获取新闻内容时发生错误，请稍后重试',
            'articles': flattened_articles,
            'currentDate': date,
            'generated_title': '获取新闻失败',
            'articles_in_html': '',
            'first_image_url': None
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

# 常用邮箱域名后缀白名单
VALID_EMAIL_SUFFIXES = {
    # 教育机构
    '.edu.cn',    # 中国教育机构
    '.edu.hk',    # 香港教育机构
    '.edu.tw',    # 台湾教育机构
    '.edu',       # 国际教育机构
    
    # 政府机构
    '.gov.cn',    # 中国政府机构
    '.gov',       # 国际政府机构
    
    # 企业邮箱
    '.com.cn',    # 中国企业
    '.net.cn',    # 中国网络
    '.org.cn',    # 中国组织
    
    # 常用邮箱服务商（完整匹配）
    'qq.com',
    '163.com',
    '126.com',
    'gmail.com',
    'outlook.com',
    'hotmail.com',
    'yahoo.com',
    'icloud.com',
    'foxmail.com',
    'sina.com',
    'sohu.com',
    'aliyun.com',
    '139.com',
    'yeah.net',
    'live.com',
    'msn.com'
    # 可以继续添加其他常用域名
}

# 一次性邮箱域名检查函数
def is_disposable_email(email):
    try:
        domain = email.split('@')[1].lower()
        
        # 1. 检查完整域名是否在白名单中
        if domain in VALID_EMAIL_SUFFIXES:
            return False
            
        # 2. 检查域名后缀
        for suffix in VALID_EMAIL_SUFFIXES:
            if suffix.startswith('.') and domain.endswith(suffix):
                return False
                
        # 3. 如果都不匹配，再检查是否是一次性邮箱
        return domain in disposable_email_domains.emails
        
    except Exception as e:
        logging.error(f"Error checking disposable email: {str(e)}")
        return True

# 邮箱格式验证函数
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    # 检查域名部分是否包含至少一个点号
    domain = email.split('@')[1]
    return '.' in domain


def _resend():
    return ResendClient(
        current_app.config['RESEND_API_KEY'],
        current_app.config['RESEND_SEGMENT_ID'],
        current_app.config['MAIL_FROM_DOMAIN'],
    )


def _send_confirmation_email(email, confirmation_link):
    _resend().send_email(
        email,
        '确认订阅 【太长不看】 科技日推',
        confirmation_email_html(confirmation_link),
        from_name='【太长不看】科技日推',
        from_local='confirm',
    )


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
            if existing_subscriber.is_subscribed:
                return jsonify({'error': '该邮箱已订阅'}), 400

            if existing_subscriber.confirmed:
                # 之前退订过：重置成待确认，重新走一遍 double opt-in
                existing_subscriber.confirmed = False
                existing_subscriber.is_active = True
                existing_subscriber.confirmation_token = secrets.token_urlsafe(32)
                existing_subscriber.save()
                
            # 重新发送确认邮件的逻辑...
            confirmation_link = url_for(
                'main.confirm_subscription',
                token=existing_subscriber.confirmation_token,
                _external=True
            )
            _send_confirmation_email(email, confirmation_link)
            return jsonify({'message': '确认邮件已重新发送，请查收'})
        
        # 创建新订阅者
        confirmation_token = secrets.token_urlsafe(32)
        subscriber = Subscriber(
            email=email,
            confirmation_token=confirmation_token,
            unsubscribe_token=secrets.token_urlsafe(32)
        )
        subscriber.save()
        
        # 发送确认邮件...
        confirmation_link = url_for(
            'main.confirm_subscription',
            token=confirmation_token,
            _external=True
        )
        _send_confirmation_email(email, confirmation_link)
        
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
            
        # 先在 Resend 设成订阅、成功了才改 Mongo。同步规则 1（Resend 退订 → Mongo 标退订）
        # 依赖"Mongo 里 confirmed 的人在 Resend 一定被设成过订阅"，所以这里失败就整体失败
        unsubscribe_token = subscriber.ensure_unsubscribe_token()
        _resend().subscribe_contact(subscriber.email, unsubscribe_token)
        subscriber.confirm_subscription()
        
        redirect_url = f"{frontend_url}/subscription/success?verified=true&token={token}"
        logging.info(f"Redirecting to: {redirect_url}")
        return redirect(redirect_url)
        
    except Exception as e:
        logging.error(f"Confirmation error: {str(e)}")
        return redirect(f"{frontend_url}/subscription/error?message=server_error")
    
    
@bp.route('/api/unsubscribe/<subscriber_id>',methods=['GET'])
def unsubscribe(subscriber_id):
    """老 Mailgun 邮件里的退订链接。只跳转到退订页，不改订阅状态：邮箱的链接安全扫描器会预先访问 GET 链接"""
    frontend_url = current_app.config['FRONTEND_URL']
    subscriber = Subscriber.objects(id=subscriber_id).first() if ObjectId.is_valid(subscriber_id) else None
    if not subscriber:
        return redirect(f"{frontend_url}/unsubscribe")
    return redirect(f"{frontend_url}/unsubscribe?token={subscriber.ensure_unsubscribe_token()}")


def _find_by_unsubscribe_token(token):
    # 只接受字符串，挡掉 {"$ne": null} 这类查询注入
    if not isinstance(token, str) or not token:
        return None
    return Subscriber.objects(unsubscribe_token=token).first()


@bp.route('/api/unsubscribe-status', methods=['GET'])
def unsubscribe_status():
    subscriber = _find_by_unsubscribe_token(request.args.get('token'))
    if not subscriber:
        return jsonify({'valid': False, 'already_unsubscribed': False})
    return jsonify({'valid': True, 'already_unsubscribed': not subscriber.is_subscribed})


@bp.route('/api/unsubscribe', methods=['POST'])
@limiter.limit("20 per hour")
def unsubscribe_by_token():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': '请求格式错误'}), 400

    subscriber = _find_by_unsubscribe_token(data.get('token'))
    if not subscriber:
        return jsonify({'error': '链接无效或已过期'}), 404
    if not subscriber.is_subscribed:
        return jsonify({'already': True})

    subscriber.unsubscribe(
        source='page',
        reasons=clean_reasons(data.get('reasons')),
        comment=clean_comment(data.get('comment')),
    )
    try:
        _resend().update_contact(subscriber.email, unsubscribed=True)
    except Exception as e:
        # 不报给用户：下次群发前的同步会把 Resend 补成退订
        logging.error(f"Resend unsubscribe failed for {subscriber.email}: {str(e)}")
        
    return jsonify({'already': False})
    
    
########################
# Email Service Routes #
########################

NEWSLETTER_FROM_NAME = '太长不看 | 科技日推'


@bp.route('/api/test/send_newsletter', methods=['POST'])
def test_send_newsletter():
    try:
        # 每调一次都占 Resend 每日的 transactional 额度，不鉴权会被刷光，确认邮件就发不出去了
        expected_key = current_app.config.get('NEWSLETTER_API_KEY')
        if not expected_key or request.headers.get('X-API-Key') != expected_key:
            return jsonify({'error': '未授权的请求'}), 401

        latest_newsletter = DailyNewsletter.objects.order_by('-date').first()
        
        if not latest_newsletter:
            return jsonify({'error': '没有找到可用的 newsletter'}), 404
            
        subject = f"[{latest_newsletter.generated_title}] {latest_newsletter.date.strftime('%Y-%m-%d')}"
        
        html_content = generate_newsletter_html(latest_newsletter, current_app.config['FRONTEND_URL'])
        # transactional 邮件不会替换 contact 占位符，换成一个一眼能看出是假的 token
        html_content = html_content.replace(UNSUBSCRIBE_TOKEN_PLACEHOLDER, 'TEST-TOKEN-NOT-REAL')
        
        test_email = "jizhoutang@outlook.com"
        email_id = _resend().send_email(
            test_email,
            subject,
            html_content,
            from_name=NEWSLETTER_FROM_NAME,
            from_local='newsletter',
        )
        
        return jsonify({
            'message': f'测试邮件已发送至 {test_email}',
            'email_id': email_id
        })
        
    except Exception as e:
        logging.error(f"Failed to send test newsletter: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    
def _send_newsletter_to_subscribers(newsletter):
    """先同步 Mongo 和 Resend，再用 Resend Broadcast 发给 segment 里所有订阅中的 contact"""
    client = _resend()

    sync_counts = None
    try:
        sync_counts = run_sync(client).counts()
    except Exception as e:
        # 同步失败不该挡住当天的简报
        logging.error(f"Subscriber sync before newsletter failed: {str(e)}")

    subscriber_count = Subscriber.get_active_subscribers().count()

    if not subscriber_count:
        return jsonify({'message': '没有已确认的订阅者'}), 200

    date_str = newsletter.date.strftime('%Y-%m-%d')
    subject = f"[{newsletter.generated_title}] {date_str}"
    html_content = generate_newsletter_html(newsletter, current_app.config['FRONTEND_URL'])

    broadcast_id = client.send_broadcast(
        subject,
        html_content,
        name=f"TLDR {date_str}",
        from_name=NEWSLETTER_FROM_NAME,
        from_local='newsletter',
    )

    newsletter.email_sent_at = datetime.utcnow()
    newsletter.email_broadcast_id = broadcast_id
    newsletter.save()

    return jsonify({
        'message': f'成功发送每日新闻给 {subscriber_count} 位订阅者',
        'date': date_str,
        'subscriber_count': subscriber_count,
        'broadcast_id': broadcast_id,
        'sync': sync_counts
    })


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

        return _send_newsletter_to_subscribers(latest_newsletter)

    except Exception as e:
        logging.error(f"Failed to send daily newsletter: {str(e)}")
        return jsonify({'error': str(e)}), 500


####################
# Vercel Cron Jobs #
####################

def _cron_auth_ok():
    """Vercel Cron 请求会自动带上 Authorization: Bearer ${CRON_SECRET}"""
    secret = current_app.config.get('CRON_SECRET')
    return bool(secret) and request.headers.get('Authorization') == f'Bearer {secret}'


@bp.route('/api/cron/generate_newsletter', methods=['GET'])
def cron_generate_newsletter():
    """定时任务一：抓取并生成当天（美东时间）的 newsletter"""
    if not _cron_auth_ok():
        return jsonify({'error': '未授权的请求'}), 401

    try:
        et = pytz.timezone('US/Eastern')
        today_et = datetime.now(et).strftime('%Y-%m-%d')
        result = get_newsletter(today_et)

        if result:
            return jsonify({
                'message': f'{today_et} 简报已就绪',
                'title': result.get('generated_title')
            })
        return jsonify({'message': f'{today_et} 暂无可用内容'}), 200

    except Exception as e:
        logging.error(f"Cron generate newsletter failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/cron/send_newsletter', methods=['GET'])
def cron_send_newsletter():
    """定时任务二：发送当天的 newsletter。当天没有新刊（周末/节假日）时跳过，避免重复发旧内容"""
    if not _cron_auth_ok():
        return jsonify({'error': '未授权的请求'}), 401

    try:
        et = pytz.timezone('US/Eastern')
        today_et = datetime.now(et).date()

        # 兜底：如果生成任务失败或没跑，这里再尝试生成一次
        get_newsletter(today_et.strftime('%Y-%m-%d'))

        latest_newsletter = DailyNewsletter.objects.order_by('-date').first()

        if not latest_newsletter:
            return jsonify({'error': '没有找到可用的 newsletter'}), 404

        if latest_newsletter.date != today_et:
            return jsonify({
                'message': f'{today_et} 无新简报（最新为 {latest_newsletter.date}），跳过发送'
            }), 200

        if latest_newsletter.email_sent_at:
            return jsonify({
                'message': f'{today_et} 的简报已于 {latest_newsletter.email_sent_at} 发送过，跳过'
            }), 200

        return _send_newsletter_to_subscribers(latest_newsletter)

    except Exception as e:
        logging.error(f"Cron send newsletter failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
########################
# Miscellaneous Routes #
@bp.route('/api/subscriber-count', methods=['GET'])
def get_subscriber_count():
    try:
        # 获取已确认且未退订的订阅者数量
        confirmed_subscribers_count = Subscriber.get_active_subscribers().count()
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
    
    
@bp.route('/api/featured-news', methods=['GET'])
def get_featured_news():
    try:
        # 获取最近的几期 newsletter（多获取几期以便筛选有图片的文章）
        latest_newsletters = DailyNewsletter.objects.order_by('-date').limit(3)
        
        if not latest_newsletters:
            return jsonify({'error': '没有找到最新内容'}), 404
            
        featured_news = {
            'company': None,
            'headlines': None,
            'future': None
        }
        
        # 用于记录每个分类是否已找到合适的文章
        found_sections = set()
        
        # 遍历最近的几期 newsletter
        for newsletter in latest_newsletters:
            for section in newsletter.sections:
                # 如果该分类已经找到文章，跳过
                if len(found_sections) == 3:
                    break
                    
                # 筛选有图片的文章
                articles_with_images = [
                    article for article in section['articles']
                    if article.get('image_url') and article['image_url'].strip()
                ]
                
                if not articles_with_images:
                    continue
                    
                first_article = articles_with_images[0]
                
                # 根据分区名称分配文章
                if section['section'] == 'Big Tech & Startups' and 'company' not in found_sections:
                    featured_news['company'] = {
                        'title': first_article.get('title', ''),
                        'content': first_article.get('content', ''),
                        'image': first_article.get('image_url', ''),
                        'date': newsletter.date.strftime('%Y-%m-%d'),
                        'url': first_article.get('url', '')
                    }
                    found_sections.add('company')
                    
                elif section['section'] == 'Miscellaneous' and 'headlines' not in found_sections:
                    featured_news['headlines'] = {
                        'title': first_article.get('title', ''),
                        'content': first_article.get('content', ''),
                        'image': first_article.get('image_url', ''),
                        'date': newsletter.date.strftime('%Y-%m-%d')
                    }
                    found_sections.add('headlines')
                    
                elif section['section'] == 'Science & Futuristic Technology' and 'future' not in found_sections:
                    featured_news['future'] = {
                        'title': first_article.get('title', ''),
                        'content': first_article.get('content', ''),
                        'image': first_article.get('image_url', ''),
                        'date': newsletter.date.strftime('%Y-%m-%d')
                    }
                    found_sections.add('future')
        
        return jsonify({
            'success': True,
            'featuredNews': featured_news
        })
        
    except Exception as e:
        logging.error(f"Error getting featured news: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


########################
# SEO Routes           #
########################

@bp.route('/api/sitemap.xml')
def sitemap():
    try:
        base_url = 'https://tldrnewsletter.cn'
        newsletters = DailyNewsletter.objects().order_by('-date').only('date')

        urls = []
        # Homepage
        urls.append(
            f'  <url>\n'
            f'    <loc>{base_url}/</loc>\n'
            f'    <changefreq>daily</changefreq>\n'
            f'    <priority>1.0</priority>\n'
            f'  </url>'
        )

        # Newsletter pages
        for nl in newsletters:
            date_str = nl.date.strftime('%Y-%m-%d')
            urls.append(
                f'  <url>\n'
                f'    <loc>{base_url}/newsletter/{date_str}</loc>\n'
                f'    <lastmod>{date_str}</lastmod>\n'
                f'    <changefreq>never</changefreq>\n'
                f'    <priority>0.8</priority>\n'
                f'  </url>'
            )

        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + '\n'.join(urls) +
            '\n</urlset>'
        )

        response = make_response(xml)
        response.headers['Content-Type'] = 'application/xml'
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response

    except Exception as e:
        logging.error(f"Error generating sitemap: {str(e)}")
        return make_response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'), 500

