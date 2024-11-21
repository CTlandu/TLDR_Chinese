import re

SECTION_EMOJI_MAP = {
    'Big Tech': '🏢',
    'Startups': '🚀',
    'Science': '🔬',
    'Programming': '👨‍💻',
    'Design': '🎨',
    'Data Science': '📊',
    'Miscellaneous': '📌',
    'Quick Links': '🔗',
    'Futuristic Technology': '🤖',
    'Tech': '💻',
    'AI': '🤖',
    'Web': '🌐',
    'Crypto': '💰',
    'Mobile': '📱',
    'Security': '🔒',
    'Cloud': '☁️',
    'Gaming': '🎮',
    'Hardware': '🔧',
    '大科技': '🏢',
    '科技': '💻',
    '创业': '🚀',
    '科学': '🔬',
    '编程': '👨‍💻',
    '设计': '🎨',
    '数据科学': '📊',
    '其他': '📌',
    '快速链接': '🔗',
    '未来科技': '🤖',
    '人工智能': '🤖',
    '网络': '🌐',
    '加密货币': '💰',
    '移动': '📱',
    '安全': '🔒',
    '云计算': '☁️',
    '游戏': '🎮',
    '硬件': '🔧'
}

TITLE_KEYWORD_EMOJI_MAP = {
    # 公司
    'Apple': '🍎',
    'Google': '🔍',
    'Microsoft': '⊞',
    'Meta': '👓',
    'Twitter': '🐦',
    'Amazon': '📦',
    'Netflix': '🎬',
    'Tesla': '🚗',
    'SpaceX': '🚀',
    'OpenAI': '🤖',
    'Android': '🤖',
    'iOS': '🍎',
    
    # 中文公司名
    '苹果': '🍎',
    '谷歌': '🔍',
    '微软': '⊞',
    '元宇宙': '👓',
    '推特': '🐦',
    '亚马逊': '📦',
    '网飞': '🎬',
    '特斯拉': '🚗',
    
    # 技术词汇
    'AI': '🤖',
    'ChatGPT': '🤖',
    'Machine Learning': '🧠',
    'Blockchain': '⛓️',
    'Bitcoin': '₿',
    'Cloud': '☁️',
    'Database': '💾',
    'API': '🔌',
    'Mobile': '📱',
    'Security': '🔒',
    'Privacy': '🔐',
    'Web': '🌐',
    'Browser': '🌐',
    'Robot': '🤖',
    'Digital': '🔢',
    'Rocket': '🚀',
    'RoboTaxi': '🤖🚕',
    'Self-driving': '🚙',
    'Autonomous': '🚙',
    
    # 中文技术词汇
    '人工智能': '🤖',
    '机器学习': '🧠',
    '区块链': '⛓️',
    '比特币': '₿',
    '云': '☁️',
    '数据库': '💾',
    '接口': '🔌',
    '移动': '📱',
    '安全': '🔒',
    '隐私': '🔐',
    '网络': '🌐',
    '浏览器': '🌐',
    '机器人': '🤖',
    '数字': '🔢',
    '火箭': '🚀',
    '自动驾驶': '🚙',
    '无人驾驶': '🚙',
    '机器人出租车': '🤖🚕',
    
    # 国家
    'USA': '🇺🇸',
    'China': '🇨🇳',
    'Japan': '🇯🇵',
    'Korea': '🇰🇷',
    'India': '🇮🇳',
    'UK': '🇬🇧',
    'Germany': '🇩🇪',
    'France': '🇫🇷',
    'Russia': '🇷🇺',
    'Canada': '🇨🇦',
    'Australia': '🇦🇺',
    'Brazil': '🇧🇷',
    
    # 中文国家名
    '美国': '🇺🇸',
    '中国': '🇨🇳',
    '日本': '🇯🇵',
    '韩国': '🇰🇷',
    '印度': '🇮🇳',
    '英国': '🇬🇧',
    '德国': '🇩🇪',
    '法国': '🇫🇷',
    '俄罗斯': '🇷🇺',
    '加拿大': '🇨🇦',
    '澳大利亚': '🇦🇺',
    '巴西': '🇧🇷'
}

def get_section_emoji(section_title):
    if any(ord(c) > 0x1F000 for c in section_title):
        return section_title
    
    for key, emoji in SECTION_EMOJI_MAP.items():
        if key.lower() in section_title.lower():
            return f"{emoji} {section_title}"
    return section_title

def get_title_emoji(title):
    if any(ord(c) > 0x1F000 for c in title):
        return title
        
    for key, emoji in TITLE_KEYWORD_EMOJI_MAP.items():
        if key.lower() in title.lower():
            return f"{emoji} {title}"
    return title

def clean_reading_time(title):
    if not title:
        return title
        
    # 更全面的正则表达式，匹配多种格式：
    patterns = [
        r'\s*\([0-9]+ (?:minute|分钟).*?\)',  # (5 minute read) 或 (5 分钟阅读)
        r'\s*\（[0-9]+ (?:minute|分钟).*?\）',  # （5 minute read）或（5 分钟阅读）- 中文括号
        r'\s*\([0-9]+(?:m|min).*?\)',  # (5m read) 或 (5min read)
        r'\s*\（[0-9]+(?:m|min).*?\）',  # （5m read）或（5min read）
        r'\s*[（(][0-9]+ ?分钟(?:阅读)?[)）]',  # (5分钟) 或 （5分钟阅读）
        r'\s*（.*?(?:分钟|minute).*?）',  # 匹配任何包含"分钟"或"minute"的中文括号内容
        r'\s*\(.*?(?:分钟|minute).*?\)',  # 匹配任何包含"分钟"或"minute"的英文括号内容
    ]
    
    # 依次应用所有模式
    for pattern in patterns:
        title = re.sub(pattern, '', title)
    
    return title.strip()  # 移除可能残留的首尾空格 