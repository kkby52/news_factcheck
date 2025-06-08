from flask import Flask, render_template
from news_utils import get_news_list_with_similarity
import os

app = Flask(__name__)

@app.route('/')
def index():
    news_list = get_news_list_with_similarity()
    return render_template('index.html', news_list=news_list)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "10000"))
    app.run(host=host, port=port)
