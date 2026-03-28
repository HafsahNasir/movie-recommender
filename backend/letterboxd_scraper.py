import requests
from bs4 import BeautifulSoup

LISTS = [
    'https://letterboxd.com/dave/list/official-top-250-narrative-feature-films/',
    'https://letterboxd.com/dave/list/letterboxd-top-250/',
    'https://letterboxd.com/films/genre/horror/by/film-popularity/',
    'https://letterboxd.com/films/genre/science-fiction/by/film-popularity/',
    'https://letterboxd.com/films/genre/drama/by/film-popularity/',
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; movie-recommender/1.0)'}


def scrape_list(url, pages=3):
    """Scrape film titles from a Letterboxd list URL (up to `pages` pages)."""
    titles = []
    for page in range(1, pages + 1):
        page_url = url if page == 1 else f"{url.rstrip('/')}/page/{page}/"
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            break
        soup = BeautifulSoup(resp.text, 'html.parser')
        posters = soup.select('li.poster-container div.film-poster img[alt]')
        if not posters:
            break
        for img in posters:
            title = img.get('alt', '').strip()
            if title:
                titles.append(title)
    return titles


def get_discovery_candidates():
    """Scrape all configured lists and return a deduplicated list of film titles."""
    seen = set()
    results = []
    for url in LISTS:
        for title in scrape_list(url):
            key = title.lower()
            if key not in seen:
                seen.add(key)
                results.append(title)
    return results
