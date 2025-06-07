from sentence_transformers import SentenceTransformer, util
from news_crawler import get_news_list

model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

news_list = get_news_list()

for i, news in enumerate(news_list):
    print(f"\n📰 뉴스 {i+1}")
    
    if news.get("is_guide"):
        print(f"📌 {news['title']}")
        continue

    title = news["title"]
    content = news["content"]

    if content == "[본문 크롤링 실패]":
        similarity = 0
    else:
        embeddings = model.encode([title, content])
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

    print("제목:", title)
    print("본문 일부:", content[:100], "...")
    print("신뢰도:", round(similarity * 100, 2), "%")
    print("이미지:", news.get("image"))
    print("링크:", news.get("url")) 