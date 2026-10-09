from conftest import load_module

feedback = load_module('api/services/unsubscribe_feedback.py')


def test_only_whitelisted_reasons_are_kept_in_order_without_duplicates():
    reasons = ['quality', 'hack', 'too_frequent', 'quality', {'$ne': 1}, None, 'other']

    assert feedback.clean_reasons(reasons) == ['quality', 'too_frequent', 'other']


def test_non_list_reasons_become_empty():
    assert feedback.clean_reasons(None) == []
    assert feedback.clean_reasons('quality') == []
    assert feedback.clean_reasons({'quality': True}) == []


def test_whitelist_matches_plan():
    assert feedback.UNSUBSCRIBE_REASONS == (
        'too_frequent', 'not_relevant', 'quality', 'read_elsewhere',
        'read_original', 'email_issue', 'no_time', 'other',
    )


def test_comment_is_trimmed_and_truncated():
    assert feedback.clean_comment('  太多了  \n') == '太多了'
    assert len(feedback.clean_comment('长' * 800)) == 500


def test_non_string_comment_becomes_empty():
    assert feedback.clean_comment(None) == ''
    assert feedback.clean_comment(['x']) == ''
