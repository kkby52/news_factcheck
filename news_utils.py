import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 📌 비선형 스케일링: 원래 0~0.15 사이 값을 0~100 사이로 자연스럽게 확장
def calculate_similarity(title, content):
    if content == "[본문 크롤링 실패]":
        return 0.0
    vectorizer = TfidfVectorizer().fit_transform([title, content])
    similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2]).item()

    # 비선형 스케일링 (예: sqrt 사용 → 너무 낮은 수치를 보완)
    adjusted = similarity ** 0.5  # √similarity
    return round(adjusted * 100, 2)


def get_news_list_with_similarity():
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    news_data = []
    seen_titles = set()
    seen_urls = set()

    articles = soup.select(".rankingnews_box a")[:30]

    for idx, article in enumerate(articles):
        title = article.get_text(strip=True)
        href = article.get("href")

        # ✅ 첫 번째 '랭킹' 제목만 안내 메시지로 출력
        if "랭킹" in title and idx == 0:
            news_data.append({
                "title": f"{title}",
                "content": None,
                "image": None,
                "url": None,
                "is_guide": True,
                "similarity": None
            })
            continue

        article_url = href if href.startswith("https") else "https://news.naver.com" + href

        if title in seen_titles or article_url in seen_urls:
            continue

        try:
            article_response = requests.get(article_url, headers=headers, timeout=10)
            article_soup = BeautifulSoup(article_response.text, "html.parser")

            real_title_tag = article_soup.select_one("#title_area > span")
            if real_title_tag:
                title = real_title_tag.get_text(strip=True)

            selectors = [
                "#articleBodyContents",
                "div#articleBody",
                "div#newsct_article",
                "article p",
                ".go_trans._article_content"
            ]

            content = ""
            for sel in selectors:
                tag = article_soup.select_one(sel)
                if tag:
                    content = tag.get_text(separator=" ", strip=True)
                    if content:
                        break

            if not content:
                paragraphs = article_soup.select("#articleBodyContents p")
                if paragraphs:
                    content = " ".join(p.get_text(strip=True) for p in paragraphs)

            if not content:
                content = "[본문 크롤링 실패]"

            img_tag = article_soup.select_one("img")
            image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

            # ✅ 7번째 뉴스 (idx==6)는 제목+이미지 출력만, 나머지는 일반 처리
            if len(news_data) == 6:
                news_data.append({
                    "title": title,
                    "content": None,
                    "image": image_url,
                    "url": None,
                    "is_guide": False,
                    "similarity": None
                })
            else:
                similarity = calculate_similarity(title, content)
                news_data.append({
                    "title": title,
                    "content": content,
                    "image": image_url,
                    "url": article_url,
                    "is_guide": False,
                    "similarity": similarity
                })

            seen_titles.add(title)
            seen_urls.add(article_url)

            if len(news_data) >= 11:  # 전체 11개까지만 수집
                break

        except Exception as e:
            print(f"[에러] {e}")
            news_data.append({
                "title": title,
                "content": "[본문 크롤링 실패]",
                "image": None,
                "url": article_url,
                "is_guide": False,
                "similarity": 0
            })

    return news_data
