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
@bp.route('/newsletter')
def show_newsletter():
    et = pytz.timezone('US/Eastern')
    current_date = datetime.now(et).strftime('%Y-%m-%d')
    articles = get_newsletter()
    dates = get_available_dates()
    return render_template('newsletter.html', emails=articles, current_date=current_date, dates=dates)

@bp.route('/newsletter/<date>')
def show_newsletter_by_date(date):
    articles = get_newsletter(date)
    dates = get_available_dates()
    return render_template('newsletter.html', emails=articles, current_date=date, dates=dates)

@bp.route('/api/newsletter/<date>')
def get_newsletter_data(date):
    articles = get_newsletter(date)
    dates = get_available_dates()
    
    return jsonify({
        'currentDate': date,
        'dates': dates,
        'articles': articles
    })
