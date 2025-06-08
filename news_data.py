import json

with open("news_cache.json", encoding="utf-8") as f:
    _cached_news = json.load(f)

def get_news_list_with_similarity():
    return _cached_news
