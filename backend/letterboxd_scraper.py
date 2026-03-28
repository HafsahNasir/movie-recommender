import os
import requests

TMDB_BASE = 'https://api.themoviedb.org/3'

# TMDB genre IDs for discovery variety
GENRE_IDS = [
    18,    # Drama
    27,    # Horror
    878,   # Science Fiction
    9648,  # Mystery
    53,    # Thriller
    10749, # Romance
    35,    # Comedy
]


def _tmdb_headers():
    token = os.environ.get('TMDB_READ_ACCESS_TOKEN', '')
    return {'Authorization': f'Bearer {token}'}


def _fetch_page(endpoint, params, page):
    resp = requests.get(
        f'{TMDB_BASE}{endpoint}',
        headers=_tmdb_headers(),
        params={**params, 'page': page, 'language': 'en-US'},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get('results', [])


def get_discovery_candidates():
    """
    Return a deduplicated list of film title strings from TMDB top-rated
    and genre-popular lists — used as the discovery candidate pool.
    """
    seen = set()
    results = []

    def add(title):
        key = title.lower().strip()
        if key and key not in seen:
            seen.add(key)
            results.append(title.strip())

    # Top-rated films (3 pages = ~60 films)
    for page in range(1, 4):
        for film in _fetch_page('/movie/top_rated', {}, page):
            add(film.get('title', ''))

    # Popular films (2 pages = ~40 films)
    for page in range(1, 3):
        for film in _fetch_page('/movie/popular', {}, page):
            add(film.get('title', ''))

    # Genre-specific popular films (1 page each)
    for genre_id in GENRE_IDS:
        for film in _fetch_page('/discover/movie', {
            'with_genres': genre_id,
            'sort_by': 'vote_count.desc',
            'vote_count.gte': 1000,
        }, page=1):
            add(film.get('title', ''))

    print(f'[discovery] {len(results)} candidates from TMDB', flush=True)
    return results
