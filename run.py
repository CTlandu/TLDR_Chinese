from flask import Flask
from Backend.routes import bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)

@app.route('/')
def home():
    return "TLDR Newsletter API is running!"