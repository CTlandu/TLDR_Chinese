# 库里只存 key，中文文案在前端 UnsubscribeView.vue
UNSUBSCRIBE_REASONS = (
    'too_frequent',
    'not_relevant',
    'quality',
    'read_elsewhere',
    'read_original',
    'email_issue',
    'no_time',
    'other',
)

COMMENT_MAX_LENGTH = 500


def clean_reasons(reasons):
    if not isinstance(reasons, list):
        return []
    cleaned = []
    for reason in reasons:
        if reason in UNSUBSCRIBE_REASONS and reason not in cleaned:
            cleaned.append(reason)
    return cleaned


def clean_comment(comment):
    if not isinstance(comment, str):
        return ''
    return comment.strip()[:COMMENT_MAX_LENGTH]
