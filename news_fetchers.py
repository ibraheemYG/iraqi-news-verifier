import datetime
from typing import List, Dict, Optional

import requests

try:
    from config import NEWSAPI_KEY, NEWSDATA_API_KEY
except Exception:
    NEWSAPI_KEY = None
    NEWSDATA_API_KEY = None


def _normalize_article(title: str, body: str, url: str, date: Optional[str]) -> Dict:
    if not date:
        date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    return {
        'title': title or '',
        'body': body or '',
        'url': url or '',
        'date': date.replace('T', ' ').replace('Z', ''),
    }


def fetch_from_newsapi(query: str = 'العراق OR Iraq', language: str = 'ar', page_size: int = 50) -> List[Dict]:
    """Fetch recent Arabic news using NewsAPI.org Everything endpoint.
    Docs: https://newsapi.org/docs/endpoints/everything
    """
    if not NEWSAPI_KEY:
        return []
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'language': language,
        'sortBy': 'publishedAt',
        'pageSize': page_size,
        'apiKey': NEWSAPI_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        out: List[Dict] = []
        for a in data.get('articles', [])[:page_size]:
            title = a.get('title') or ''
            desc = a.get('description') or ''
            content = a.get('content') or ''
            body = f"{desc}\n{content}".strip()
            url = a.get('url') or ''
            date = a.get('publishedAt') or ''
            if title and url:
                out.append(_normalize_article(title, body, url, date))
        return out
    except Exception as e:
        print('NewsAPI fetch error:', e)
        return []


def fetch_from_newsdata(query: str = 'العراق', language: str = 'ar', country: str = 'iq', page_size: int = 50) -> List[Dict]:
    """Fetch recent Arabic news using NewsData.io API with graceful fallbacks.
    Docs: https://newsdata.io/documentation
    Strategy:
      - Try with language+country first
      - If 422/validation error, retry without country
      - If still failing, retry with only query
    """
    if not NEWSDATA_API_KEY:
        return []

    def _call(params: Dict) -> Optional[List[Dict]]:
        try:
            r = requests.get('https://newsdata.io/api/1/news', params=params, timeout=20)
            if r.status_code == 422:
                # Validation error with provided filters
                return None
            r.raise_for_status()
            data = r.json()
            out: List[Dict] = []
            for a in data.get('results', [])[:page_size]:
                title = a.get('title') or ''
                content = a.get('content') or ''
                desc = a.get('description') or ''
                body = f"{desc}\n{content}".strip()
                url = a.get('link') or ''
                date = a.get('pubDate') or ''
                if title and url:
                    out.append(_normalize_article(title, body, url, date))
            return out
        except Exception as e:
            print('NewsData fetch error:', e)
            return []

    # 1) Try with language + country
    params = {
        'apikey': NEWSDATA_API_KEY,
        'q': query,
        'language': language,
        'country': country,
        'page': 1,
    }
    result = _call(params)
    if result is not None:
        return result

    # 2) Retry without country
    params2 = {
        'apikey': NEWSDATA_API_KEY,
        'q': query,
        'language': language,
        'page': 1,
    }
    result2 = _call(params2)
    if result2 is not None:
        return result2

    # 3) Retry with only query
    params3 = {
        'apikey': NEWSDATA_API_KEY,
        'q': query,
        'page': 1,
    }
    result3 = _call(params3)
    return result3 or []


def fetch_all_external(limit_each: int = 50) -> List[Dict]:
    """Fetch from both sources and merge results (dedupe by URL)."""
    newsapi_items = fetch_from_newsapi(page_size=limit_each)
    newsdata_items = fetch_from_newsdata(page_size=limit_each)
    merged: Dict[str, Dict] = {}
    for item in newsapi_items + newsdata_items:
        if item.get('url') and item['url'] not in merged:
            merged[item['url']] = item
    results = list(merged.values())
    print(f"External news fetched: {len(results)} (NewsAPI {len(newsapi_items)}, NewsData {len(newsdata_items)})")
    return results
