from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "TLDR Newsletter API is running!"

@app.route('/api/newsletter/<date>')
def get_newsletter_data(date):
    return {"message": "Test successful", "date": date}