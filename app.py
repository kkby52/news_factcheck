from flask import Flask, render_template
from news_crawler import get_news_list
from sentence_transformers import SentenceTransformer, util
import os

app = Flask(__name__)
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

@app.route('/')
def index():
    news_list = get_news_list()

    for news in news_list:
        if news.get("is_guide") or news["content"] == "[본문 크롤링 실패]":
            news["similarity"] = 0
            continue

        title = news["title"]
        content = news["content"]
        embeddings = model.encode([title, content])
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
        news["similarity"] = round(similarity * 100, 2)

    return render_template('index.html', news_list=news_list)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
