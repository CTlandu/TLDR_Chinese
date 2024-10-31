from flask import Blueprint, render_template, jsonify
from .services.newsletter import get_newsletter
from datetime import datetime
import pytz
from datetime import timedelta
from flask_cors import CORS


bp = Blueprint('main', __name__)

def get_available_dates(days=7):
    et = pytz.timezone('US/Eastern')
    dates = []
    current = datetime.now(et)
    
    for i in range(days):
        date = current - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    return dates

@bp.route('/')

@bp.route('/api/newsletter/<date>')
def get_newsletter_by_date(date):
    articles = get_newsletter(date)
    dates = get_available_dates()
    
    response = {
        'articles': articles,
        'currentDate': date,
        'dates': dates
    }
    
    return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}
