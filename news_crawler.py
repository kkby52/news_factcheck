import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_news_list():
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    news_data = []
    seen_titles = set()
    seen_urls = set()

    articles = soup.select(".rankingnews_box a")[:30]  # 넉넉하게 수집

    for idx, article in enumerate(articles):
        title = article.get_text(strip=True)
        href = article.get("href")

        # 첫 번째 가이드 뉴스
        if "랭킹" in title and idx == 0:
            news_data.append({
                "title": f"{title}",
                "content": None,
                "image": None,
                "url": None,
                "is_guide": True
            })
            continue

        article_url = href if href.startswith("https") else "https://news.naver.com" + href

        # 중복 제거
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

            news_data.append({
                "title": title,
                "content": content,
                "image": image_url,
                "url": article_url,
                "is_guide": False
            })

            seen_titles.add(title)
            seen_urls.add(article_url)

            if len(news_data) >= 30:  # 가이드 1개 + 기사 10개
                break

        except Exception as e:
            print(f"[에러] 본문 크롤링 실패: {e}")
            news_data.append({
                "title": title,
                "content": "[본문 크롤링 실패]",
                "image": None,
                "url": article_url,
                "is_guide": False
            })
            seen_titles.add(title)
            seen_urls.add(article_url)

    return news_data


def print_news_with_similarity(news_list):
    model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

    for i, news in enumerate(news_list):
        print(f"\n📰 뉴스 {i+1}")

        title = news["title"]

        # 첫 번째 뉴스는 제외하고, 7번째마다 (index 6, 12, ...) 안내 메시지 출력
        if i % 6 == 0 and i != 0:
            print(f"📌 오늘의 {title} 랭킹 결과를 더 볼 수 있어요.")
            continue

        if news.get("is_guide"):
            print(f"📌 오늘의 {title}")
            continue

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


if __name__ == "__main__":
    news_list = get_news_list()
    print_news_with_similarity(news_list)
