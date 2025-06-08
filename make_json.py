import json
from sentence_transformers import SentenceTransformer, util
import requests
from bs4 import BeautifulSoup

# 모델 불러오기 (한 번만)
model = SentenceTransformer("monologg/koelectra-base-v3-nli")

def calculate_similarity(title, content):
    if content == "[본문 크롤링 실패]":
        return 0.0
    embeddings = model.encode([title, content])
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(similarity * 100, 2)

def crawl_news_and_save():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = soup.select(".rankingnews_box a")[:30]

    result = []
    seen = set()

    for idx, article in enumerate(articles):
        title = article.get_text(strip=True)
        href = article.get("href")

        if "랭킹" in title and idx == 0:
            result.append({
                "title": title,
                "content": None,
                "image": None,
                "url": None,
                "is_guide": True,
                "similarity": None
            })
            continue

        article_url = href if href.startswith("http") else "https://news.naver.com" + href
        if title in seen:
            continue

        try:
            article_resp = requests.get(article_url, headers=headers, timeout=10)
            article_soup = BeautifulSoup(article_resp.text, "html.parser")
            content = ""
            selectors = ["#articleBodyContents", "div#articleBody", "div#newsct_article"]
            for sel in selectors:
                tag = article_soup.select_one(sel)
                if tag:
                    content = tag.get_text(" ", strip=True)
                    break
            if not content:
                content = "[본문 크롤링 실패]"
        except:
            content = "[본문 크롤링 실패]"

        similarity = calculate_similarity(title, content)

        result.append({
            "title": title,
            "content": content,
            "image": None,
            "url": article_url,
            "is_guide": False,
            "similarity": similarity
        })
        seen.add(title)
        if len(result) >= 11:
            break

    # 저장
    with open("news_cache.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("저장 완료!")

crawl_news_and_save()
