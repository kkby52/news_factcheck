# app.py
from flask import Flask, jsonify, render_template
from news_data import get_news_list_with_similarity

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', news=get_news_list_with_similarity())

@app.route('/api/news')
def api_news():
    return jsonify(get_news_list_with_similarity())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
