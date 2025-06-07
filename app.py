from flask import Flask, render_template
from news_crawler import get_news_list

import os

app = Flask(__name__)

@app.route('/')
def index():
    news = get_news_list()
    return render_template('index.html', news_list=news)

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    
    app.run(host="0.0.0.0", port=port)
