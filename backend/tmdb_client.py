import json
import os
import requests


class TMDBClient:
    BASE = 'https://api.themoviedb.org/3'
    IMG_BASE = 'https://image.tmdb.org/t/p/w500'

    def __init__(self, token, cache_path='tmdb_cache.json'):
        self.headers = {'Authorization': f'Bearer {token}'}
        self.cache_path = cache_path
        self._cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path) as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_path, 'w') as f:
            json.dump(self._cache, f)

    def _get(self, path, params=None):
        resp = requests.get(f'{self.BASE}{path}', headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_movie(self, title, year):
        """Return enriched movie dict or None if not found. Results are disk-cached."""
        cache_key = f'{title.lower()}|{year}'
        if cache_key in self._cache:
            return self._cache[cache_key]

        search = self._get('/search/movie', {'query': title, 'year': year, 'language': 'en-US'})
        if not search['results']:
            return None

        hit = search['results'][0]
        tmdb_id = hit['id']

        details = self._get(f'/movie/{tmdb_id}', {'language': 'en-US'})
        credits = self._get(f'/movie/{tmdb_id}/credits', {'language': 'en-US'})

        director = next(
            (p['name'] for p in credits.get('crew', []) if p['job'] == 'Director'),
            'Unknown'
        )
        cast = [p['name'] for p in sorted(credits.get('cast', []), key=lambda x: x.get('order', 99))[:5]]
        genres = [g['name'] for g in details.get('genres', [])]
        poster = f"{self.IMG_BASE}{hit['poster_path']}" if hit.get('poster_path') else None

        result = {
            'tmdb_id': tmdb_id,
            'title': hit['title'],
            'year': int(hit['release_date'][:4]) if hit.get('release_date') else year,
            'overview': hit.get('overview', ''),
            'poster_url': poster,
            'tmdb_rating': round(hit.get('vote_average', 0) / 2, 1),
            'runtime': details.get('runtime'),
            'genres': genres,
            'director': director,
            'cast': cast,
        }

        self._cache[cache_key] = result
        self._save_cache()
        return result
