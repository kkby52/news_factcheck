from flask import Flask, render_template
from news_crawler import get_news_list

app = Flask(__name__)

@app.route('/')
def index():
    news = get_news_list()
    return render_template('index.html', news_list=news)

if __name__ == '__main__':
    app.run(debug=True)
