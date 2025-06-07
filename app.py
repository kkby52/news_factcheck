from flask import Flask, render_template
from news_crawler import get_naver_news_titles  # 위 코드를 news_crawler.py로 저장했다고 가정

app = Flask(__name__)

@app.route('/')
def index():
    news = get_naver_news_titles()
    return render_template('index.html', news_list=news)

if __name__ == '__main__':
    app.run(debug=True) 