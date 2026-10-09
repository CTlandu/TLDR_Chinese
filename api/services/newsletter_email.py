# Resend Broadcast 发送时会把它替换成每个 contact 自己的 unsubscribe_token 属性
UNSUBSCRIBE_TOKEN_PLACEHOLDER = '{{{contact.unsubscribe_token}}}'


def confirmation_email_html(confirmation_link):
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


def generate_newsletter_html(newsletter, frontend_url):
    newsletter_date = newsletter.date.strftime('%Y-%m-%d')
    newsletter_title = newsletter.generated_title
    unsubscribe_url = f"{frontend_url.rstrip('/')}/unsubscribe?token={UNSUBSCRIBE_TOKEN_PLACEHOLDER}"

    html = f"""
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2c3e50; font-size: 24px; margin: 0; padding: 20px 0; border-bottom: 2px solid #eee;">
                    {newsletter_title}
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

    for section in newsletter.sections:
        html += f"""
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #2c3e50; font-size: 20px; margin: 0 0 20px 0;
                            padding-bottom: 10px; border-bottom: 2px solid #eee;">
                        {section['section']}
                    </h2>
            """

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
                    <a href="{unsubscribe_url}"
                    style="color: #3498db; text-decoration: none;">
                        取消订阅
                    </a>
                </p>
            </div>
        </div>
        """

    return html
