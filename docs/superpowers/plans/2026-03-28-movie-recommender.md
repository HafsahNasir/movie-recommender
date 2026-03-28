# Movie Recommender Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local web app that reads hafsahnasir's Letterboxd data, scores unwatched films against her taste profile, and recommends 6 films with Gemini-generated "why you'd like it" blurbs in a Deep Space liquid glass UI.

**Architecture:** Python Flask backend exposes a single `GET /api/recommend` endpoint. It reads Letterboxd CSV exports + scrapes popular Letterboxd lists, scores candidates using a taste profile built from 4★+ rated films, enforces diversity across the 6 picks, enriches with TMDB metadata, and calls Gemini once per shuffle for personalised blurbs. React + Vite frontend renders a Hero card + row of 5 with a card-flip shuffle animation.

**Tech Stack:** Python 3.11, Flask, requests, BeautifulSoup4, google-generativeai, React 18, Vite, axios, plain CSS

---

## File Map

```
movie_recommender/
├── backend/
│   ├── app.py                  # Flask server — /api/recommend, /api/stats
│   ├── letterboxd_parser.py    # parse ratings.csv, watchlist.csv, watched.csv
│   ├── letterboxd_scraper.py   # scrape popular Letterboxd list URLs → film slugs
│   ├── taste_profile.py        # build genre/director/actor/era weights from ratings
│   ├── recommender.py          # score candidates, enforce diversity, return 6
│   ├── tmdb_client.py          # TMDB search + credits + poster; disk-cached
│   ├── gemini_client.py        # batch-generate "why you'd like it" blurbs
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx            # React entry point
│   │   ├── App.jsx             # root component — fetches data, manages state
│   │   ├── index.css           # Deep Space theme, glass utilities, blob animation
│   │   └── components/
│   │       ├── HeroCard.jsx    # large featured film card
│   │       ├── MovieCard.jsx   # small card in row of 5
│   │       └── ShuffleButton.jsx # pill button, triggers flip animation
│   ├── package.json
│   └── vite.config.js          # proxies /api → http://localhost:5000
├── data/                       # user drops Letterboxd CSV exports here
│   └── .gitkeep
├── tests/
│   ├── test_letterboxd_parser.py
│   ├── test_tmdb_client.py
│   ├── test_taste_profile.py
│   ├── test_recommender.py
│   ├── test_gemini_client.py
│   ├── test_app.py
│   └── fixtures/
│       ├── ratings.csv
│       └── watchlist.csv
├── .env                        # gitignored — real keys
├── .env.example                # committed — key names only
└── .gitignore
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `data/.gitkeep`
- Create: `tests/fixtures/ratings.csv`
- Create: `tests/fixtures/watchlist.csv`

- [ ] **Step 1: Create backend/requirements.txt**

```
flask==3.0.3
flask-cors==4.0.1
requests==2.32.3
beautifulsoup4==4.12.3
google-generativeai==0.7.2
python-dotenv==1.0.1
pytest==8.2.2
```

- [ ] **Step 2: Create .env.example**

```
TMDB_READ_ACCESS_TOKEN=your_tmdb_read_access_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

- [ ] **Step 3: Create .gitignore**

```
.env
__pycache__/
*.pyc
.pytest_cache/
node_modules/
dist/
.superpowers/
tmdb_cache.json
```

- [ ] **Step 4: Create .env with real keys**

```
TMDB_READ_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlZjg4MzIyNDBlZjUyOTgzOWUxNGYwMDIyOWE2Y2YzZSIsIm5iZiI6MTcyMDQ2NzI4Mi42MDUsInN1YiI6IjY2OGMzZjUyYTJiOGEyYzRmNjU2ZjM4NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LALR13edPTq7MrJlk_Iq6itZKfJkWD85-izLs9HbOJM
GEMINI_API_KEY=AIzaSyBK0QhVBT5j-rb45IyAuguVqcsnMjKj1ig
```

- [ ] **Step 5: Create test fixture data**

`tests/fixtures/ratings.csv`:
```csv
Date,Name,Year,Letterboxd URI,Rating
2024-01-15,Mulholland Drive,2001,https://letterboxd.com/film/mulholland-drive/,5.0
2024-01-10,Chungking Express,1994,https://letterboxd.com/film/chungking-express/,5.0
2024-01-05,Persona,1966,https://letterboxd.com/film/persona/,4.5
2023-12-20,Parasite,2019,https://letterboxd.com/film/parasite-2019/,4.5
2023-12-10,Hereditary,2018,https://letterboxd.com/film/hereditary/,4.0
2023-11-30,The Favourite,2018,https://letterboxd.com/film/the-favourite/,4.0
2023-11-20,Portrait of a Lady on Fire,2019,https://letterboxd.com/film/portrait-of-a-lady-on-fire/,3.5
2023-11-10,Avengers: Endgame,2019,https://letterboxd.com/film/avengers-endgame/,2.5
```

`tests/fixtures/watchlist.csv`:
```csv
Date,Name,Year,Letterboxd URI
2024-02-01,In the Mood for Love,2000,https://letterboxd.com/film/in-the-mood-for-love/
2024-01-25,The Seventh Seal,1957,https://letterboxd.com/film/the-seventh-seal/
2024-01-20,Stalker,1979,https://letterboxd.com/film/stalker/
```

- [ ] **Step 6: Create data/.gitkeep and install backend deps**

```bash
touch data/.gitkeep
cd backend && pip install -r requirements.txt
```

Expected: packages install without errors.

- [ ] **Step 7: Initialise git and commit scaffold**

```bash
git init
git add .gitignore .env.example backend/requirements.txt data/.gitkeep tests/
git commit -m "chore: project scaffold — deps, env template, test fixtures"
```

---

## Task 2: Letterboxd CSV Parser

**Files:**
- Create: `backend/letterboxd_parser.py`
- Create: `tests/test_letterboxd_parser.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_letterboxd_parser.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from letterboxd_parser import parse_ratings, parse_watchlist, get_watched_titles

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


def test_parse_ratings_returns_list_of_dicts():
    ratings = parse_ratings(os.path.join(FIXTURES, 'ratings.csv'))
    assert isinstance(ratings, list)
    assert len(ratings) == 8


def test_parse_ratings_fields():
    ratings = parse_ratings(os.path.join(FIXTURES, 'ratings.csv'))
    first = ratings[0]
    assert first['title'] == 'Mulholland Drive'
    assert first['year'] == 2001
    assert first['rating'] == 5.0


def test_parse_ratings_high_rated_only():
    ratings = parse_ratings(os.path.join(FIXTURES, 'ratings.csv'), min_rating=4.0)
    assert all(r['rating'] >= 4.0 for r in ratings)
    assert len(ratings) == 6


def test_parse_watchlist_returns_titles():
    watchlist = parse_watchlist(os.path.join(FIXTURES, 'watchlist.csv'))
    assert isinstance(watchlist, list)
    assert len(watchlist) == 3
    assert watchlist[0]['title'] == 'In the Mood for Love'
    assert watchlist[0]['year'] == 2000


def test_get_watched_titles_combines_rated_and_unrated():
    watched = get_watched_titles(os.path.join(FIXTURES, 'ratings.csv'))
    assert 'Mulholland Drive' in watched
    assert 'Avengers: Endgame' in watched


def test_get_watched_titles_returns_set():
    watched = get_watched_titles(os.path.join(FIXTURES, 'ratings.csv'))
    assert isinstance(watched, set)
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd /path/to/movie_recommender
pytest tests/test_letterboxd_parser.py -v
```

Expected: `ModuleNotFoundError: No module named 'letterboxd_parser'`

- [ ] **Step 3: Implement letterboxd_parser.py**

`backend/letterboxd_parser.py`:
```python
import csv


def parse_ratings(path, min_rating=0.0):
    """Return list of {title, year, rating} from ratings.csv."""
    results = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                rating = float(row['Rating']) if row['Rating'] else 0.0
            except ValueError:
                rating = 0.0
            if rating >= min_rating:
                results.append({
                    'title': row['Name'].strip(),
                    'year': int(row['Year']) if row['Year'] else None,
                    'rating': rating,
                })
    return results


def parse_watchlist(path):
    """Return list of {title, year} from watchlist.csv."""
    results = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            results.append({
                'title': row['Name'].strip(),
                'year': int(row['Year']) if row['Year'] else None,
            })
    return results


def get_watched_titles(ratings_path):
    """Return set of all watched film titles (lowercased for comparison)."""
    titles = set()
    with open(ratings_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            titles.add(row['Name'].strip().lower())
    return titles
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_letterboxd_parser.py -v
```

Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/letterboxd_parser.py tests/test_letterboxd_parser.py
git commit -m "feat: letterboxd CSV parser"
```

---

## Task 3: TMDB Client with Disk Cache

**Files:**
- Create: `backend/tmdb_client.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_letterboxd_parser.py` a new file — actually create `tests/test_tmdb_client.py`:

```python
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch, MagicMock
from tmdb_client import TMDBClient


def make_client(tmp_path):
    return TMDBClient(token='fake_token', cache_path=str(tmp_path / 'cache.json'))


def mock_search_response(title, year, tmdb_id=12345):
    return {
        'results': [{
            'id': tmdb_id,
            'title': title,
            'release_date': f'{year}-01-01',
            'overview': 'A great film.',
            'poster_path': '/abc123.jpg',
            'vote_average': 8.2,
        }]
    }


def mock_credits_response():
    return {
        'crew': [{'job': 'Director', 'name': 'Test Director'}],
        'cast': [
            {'name': 'Actor One', 'order': 0},
            {'name': 'Actor Two', 'order': 1},
            {'name': 'Actor Three', 'order': 2},
        ]
    }


def mock_details_response(tmdb_id=12345):
    return {
        'id': tmdb_id,
        'genres': [{'name': 'Drama'}, {'name': 'Mystery'}],
        'runtime': 120,
    }


def test_get_movie_returns_enriched_dict(tmp_path):
    client = make_client(tmp_path)
    with patch.object(client, '_get') as mock_get:
        mock_get.side_effect = [
            mock_search_response('Mulholland Drive', 2001),
            mock_details_response(),
            mock_credits_response(),
        ]
        result = client.get_movie('Mulholland Drive', 2001)

    assert result['title'] == 'Mulholland Drive'
    assert result['tmdb_id'] == 12345
    assert result['director'] == 'Test Director'
    assert 'Drama' in result['genres']
    assert result['runtime'] == 120
    assert result['poster_url'] == 'https://image.tmdb.org/t/p/w500/abc123.jpg'
    assert result['cast'] == ['Actor One', 'Actor Two', 'Actor Three']


def test_get_movie_caches_result(tmp_path):
    client = make_client(tmp_path)
    with patch.object(client, '_get') as mock_get:
        mock_get.side_effect = [
            mock_search_response('Mulholland Drive', 2001),
            mock_details_response(),
            mock_credits_response(),
        ]
        client.get_movie('Mulholland Drive', 2001)

    # Second call — _get should NOT be called again
    with patch.object(client, '_get') as mock_get2:
        result = client.get_movie('Mulholland Drive', 2001)
        mock_get2.assert_not_called()

    assert result['title'] == 'Mulholland Drive'


def test_get_movie_returns_none_when_not_found(tmp_path):
    client = make_client(tmp_path)
    with patch.object(client, '_get') as mock_get:
        mock_get.return_value = {'results': []}
        result = client.get_movie('Nonexistent Film', 1800)
    assert result is None
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_tmdb_client.py -v
```

Expected: `ModuleNotFoundError: No module named 'tmdb_client'`

- [ ] **Step 3: Implement tmdb_client.py**

`backend/tmdb_client.py`:
```python
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
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_tmdb_client.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/tmdb_client.py tests/test_tmdb_client.py
git commit -m "feat: TMDB client with disk cache"
```

---

## Task 4: Letterboxd List Scraper

**Files:**
- Create: `backend/letterboxd_scraper.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_letterboxd_scraper.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch
from letterboxd_scraper import scrape_list, get_discovery_candidates

SAMPLE_HTML = """
<html><body>
<ul class="poster-list">
  <li class="poster-container">
    <div class="film-poster" data-film-slug="mulholland-drive"
         data-film-id="1018" data-target-link="/film/mulholland-drive/">
      <img alt="Mulholland Drive" />
    </div>
  </li>
  <li class="poster-container">
    <div class="film-poster" data-film-slug="chungking-express"
         data-film-id="11776" data-target-link="/film/chungking-express/">
      <img alt="Chungking Express" />
    </div>
  </li>
</ul>
</body></html>
"""


def test_scrape_list_returns_titles():
    with patch('letterboxd_scraper.requests.get') as mock_get:
        mock_get.return_value.text = SAMPLE_HTML
        mock_get.return_value.raise_for_status = lambda: None
        results = scrape_list('https://letterboxd.com/films/')
    assert 'Mulholland Drive' in results
    assert 'Chungking Express' in results


def test_scrape_list_returns_list_of_strings():
    with patch('letterboxd_scraper.requests.get') as mock_get:
        mock_get.return_value.text = SAMPLE_HTML
        mock_get.return_value.raise_for_status = lambda: None
        results = scrape_list('https://letterboxd.com/films/')
    assert isinstance(results, list)
    assert all(isinstance(t, str) for t in results)


def test_get_discovery_candidates_deduplicates():
    with patch('letterboxd_scraper.scrape_list', return_value=['Film A', 'Film A', 'Film B']):
        results = get_discovery_candidates()
    assert results.count('Film A') == 1
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_letterboxd_scraper.py -v
```

Expected: `ModuleNotFoundError: No module named 'letterboxd_scraper'`

- [ ] **Step 3: Implement letterboxd_scraper.py**

`backend/letterboxd_scraper.py`:
```python
import requests
from bs4 import BeautifulSoup

# Popular Letterboxd lists to draw discovery candidates from
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
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_letterboxd_scraper.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/letterboxd_scraper.py tests/test_letterboxd_scraper.py
git commit -m "feat: letterboxd list scraper"
```

---

## Task 5: Taste Profile Builder

**Files:**
- Create: `backend/taste_profile.py`
- Create: `tests/test_taste_profile.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_taste_profile.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import MagicMock
from taste_profile import build_profile

def make_tmdb(genre_map):
    """Return a mock TMDBClient whose get_movie returns preset data."""
    client = MagicMock()
    def get_movie(title, year):
        return genre_map.get(title)
    client.get_movie.side_effect = get_movie
    return client


def test_profile_genre_weights():
    tmdb = make_tmdb({
        'Film A': {'genres': ['Drama', 'Mystery'], 'director': 'Dir A', 'cast': ['Actor 1'], 'year': 2001},
        'Film B': {'genres': ['Drama', 'Horror'],  'director': 'Dir B', 'cast': ['Actor 2'], 'year': 2005},
        'Film C': {'genres': ['Comedy'],            'director': 'Dir C', 'cast': ['Actor 3'], 'year': 2010},
    })
    ratings = [
        {'title': 'Film A', 'year': 2001, 'rating': 5.0},
        {'title': 'Film B', 'year': 2005, 'rating': 4.5},
        {'title': 'Film C', 'year': 2010, 'rating': 2.0},  # below threshold
    ]
    profile = build_profile(ratings, tmdb)
    assert profile['genres']['Drama'] == 2
    assert profile['genres']['Mystery'] == 1
    assert profile['genres']['Horror'] == 1
    assert 'Comedy' not in profile['genres']


def test_profile_director_affinity():
    tmdb = make_tmdb({
        'Film A': {'genres': ['Drama'], 'director': 'David Lynch', 'cast': [], 'year': 2001},
    })
    ratings = [{'title': 'Film A', 'year': 2001, 'rating': 5.0}]
    profile = build_profile(ratings, tmdb)
    assert profile['directors']['David Lynch'] == 1


def test_profile_era_weights():
    tmdb = make_tmdb({
        'Old Film': {'genres': ['Drama'], 'director': 'D', 'cast': [], 'year': 1966},
        'New Film': {'genres': ['Drama'], 'director': 'D', 'cast': [], 'year': 2019},
    })
    ratings = [
        {'title': 'Old Film', 'year': 1966, 'rating': 4.5},
        {'title': 'New Film', 'year': 2019, 'rating': 4.5},
    ]
    profile = build_profile(ratings, tmdb)
    assert profile['eras']['1960s'] == 1
    assert profile['eras']['2010s'] == 1


def test_profile_summary_string():
    tmdb = make_tmdb({
        'Film A': {'genres': ['Drama'], 'director': 'David Lynch', 'cast': ['Actor X'], 'year': 2001},
    })
    ratings = [{'title': 'Film A', 'year': 2001, 'rating': 5.0}]
    profile = build_profile(ratings, tmdb)
    assert isinstance(profile['summary'], str)
    assert 'Drama' in profile['summary']
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_taste_profile.py -v
```

Expected: `ModuleNotFoundError: No module named 'taste_profile'`

- [ ] **Step 3: Implement taste_profile.py**

`backend/taste_profile.py`:
```python
from collections import Counter


MIN_RATING = 4.0


def _decade(year):
    if not year:
        return 'Unknown'
    return f"{(year // 10) * 10}s"


def build_profile(ratings, tmdb_client):
    """
    Build a taste profile from a list of rated films.

    ratings: list of {title, year, rating}
    tmdb_client: TMDBClient instance

    Returns:
        {
            genres: Counter,
            directors: Counter,
            actors: Counter,
            eras: Counter,
            high_rated_titles: list[str],
            summary: str,
        }
    """
    genres = Counter()
    directors = Counter()
    actors = Counter()
    eras = Counter()
    high_rated_titles = []

    for item in ratings:
        if item['rating'] < MIN_RATING:
            continue
        data = tmdb_client.get_movie(item['title'], item['year'])
        if not data:
            continue
        high_rated_titles.append(item['title'])
        for g in data.get('genres', []):
            genres[g] += 1
        director = data.get('director')
        if director and director != 'Unknown':
            directors[director] += 1
        for actor in data.get('cast', [])[:3]:
            actors[actor] += 1
        eras[_decade(data.get('year') or item.get('year'))] += 1

    top_genres = [g for g, _ in genres.most_common(5)]
    top_directors = [d for d, _ in directors.most_common(3)]
    example_titles = high_rated_titles[:5]

    summary = (
        f"Loves {', '.join(top_genres) if top_genres else 'various genres'}. "
        f"Favourite directors include {', '.join(top_directors) if top_directors else 'various directors'}. "
        f"Highly rated: {', '.join(example_titles)}."
    )

    return {
        'genres': genres,
        'directors': directors,
        'actors': actors,
        'eras': eras,
        'high_rated_titles': high_rated_titles,
        'summary': summary,
    }
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_taste_profile.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/taste_profile.py tests/test_taste_profile.py
git commit -m "feat: taste profile builder"
```

---

## Task 6: Recommender — Scoring + Diversity Enforcement

**Files:**
- Create: `backend/recommender.py`
- Create: `tests/test_recommender.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_recommender.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from collections import Counter
from recommender import score_candidate, pick_six

PROFILE = {
    'genres': Counter({'Drama': 5, 'Mystery': 3, 'Horror': 2}),
    'directors': Counter({'David Lynch': 3}),
    'actors': Counter({'Naomi Watts': 2}),
    'eras': Counter({'2000s': 4, '1990s': 2}),
    'high_rated_titles': ['Mulholland Drive', 'Persona'],
    'summary': 'Loves Drama, Mystery.',
}

CANDIDATE_DRAMA = {
    'title': 'Inland Empire', 'year': 2006,
    'genres': ['Drama', 'Mystery'], 'director': 'David Lynch',
    'cast': ['Laura Dern'], 'source': 'discovered',
}
CANDIDATE_COMEDY = {
    'title': 'Some Comedy', 'year': 2020,
    'genres': ['Comedy', 'Romance'], 'director': 'Unknown',
    'cast': [], 'source': 'discovered',
}


def test_score_candidate_higher_for_matching_genres():
    score_drama = score_candidate(CANDIDATE_DRAMA, PROFILE)
    score_comedy = score_candidate(CANDIDATE_COMEDY, PROFILE)
    assert score_drama > score_comedy


def test_score_candidate_higher_for_matching_director():
    with_director = {**CANDIDATE_DRAMA, 'director': 'David Lynch'}
    without_director = {**CANDIDATE_DRAMA, 'director': 'Someone Else'}
    assert score_candidate(with_director, PROFILE) > score_candidate(without_director, PROFILE)


def test_pick_six_returns_six():
    candidates = [
        {**CANDIDATE_DRAMA, 'title': f'Film {i}', 'genres': ['Drama' if i % 2 == 0 else 'Horror'],
         'source': 'watchlist' if i < 3 else 'discovered', 'year': 1990 + i}
        for i in range(20)
    ]
    result = pick_six(candidates, PROFILE)
    assert len(result) == 6


def test_pick_six_includes_watchlist_and_discovered():
    candidates = [
        {**CANDIDATE_DRAMA, 'title': f'WL {i}', 'genres': ['Drama'], 'source': 'watchlist', 'year': 2000 + i}
        for i in range(5)
    ] + [
        {**CANDIDATE_DRAMA, 'title': f'DS {i}', 'genres': ['Mystery'], 'source': 'discovered', 'year': 1990 + i}
        for i in range(5)
    ]
    result = pick_six(candidates, PROFILE)
    sources = [r['source'] for r in result]
    assert sources.count('watchlist') >= 2
    assert sources.count('discovered') >= 2


def test_pick_six_genre_diversity():
    genres_pool = ['Drama', 'Horror', 'Sci-Fi', 'Comedy', 'Thriller']
    candidates = [
        {**CANDIDATE_DRAMA, 'title': f'Film {i}', 'genres': [genres_pool[i % 5]],
         'source': 'watchlist' if i < 3 else 'discovered', 'year': 2000 + i}
        for i in range(15)
    ]
    result = pick_six(candidates, PROFILE)
    all_genres = set(g for film in result for g in film['genres'])
    assert len(all_genres) >= 3
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_recommender.py -v
```

Expected: `ModuleNotFoundError: No module named 'recommender'`

- [ ] **Step 3: Implement recommender.py**

`backend/recommender.py`:
```python
import random
from collections import Counter


def score_candidate(candidate, profile):
    """Score a candidate film against the user's taste profile."""
    score = 0.0
    genres = profile['genres']
    directors = profile['directors']
    actors = profile['actors']
    eras = profile['eras']

    for genre in candidate.get('genres', []):
        score += genres.get(genre, 0) * 2.0

    director = candidate.get('director', '')
    score += directors.get(director, 0) * 3.0

    for actor in candidate.get('cast', []):
        score += actors.get(actor, 0) * 1.5

    decade = f"{(candidate['year'] // 10) * 10}s" if candidate.get('year') else None
    if decade:
        score += eras.get(decade, 0) * 0.5

    # Small random jitter to vary results between shuffles
    score += random.uniform(0, 0.5)

    return score


def pick_six(candidates, profile):
    """
    Pick 6 films from candidates with diversity enforcement.

    Rules:
    - At least 2 from watchlist, at least 2 from discovered
    - At least 3 different genres across the 6
    - Prefer at least 1 pre-2000 film (soft constraint)
    """
    scored = sorted(candidates, key=lambda c: score_candidate(c, profile), reverse=True)

    watchlist = [c for c in scored if c.get('source') == 'watchlist']
    discovered = [c for c in scored if c.get('source') == 'discovered']

    selected = []
    used_genres = set()

    # Guarantee at least 2 watchlist and 2 discovered
    for pool in [watchlist[:2], discovered[:2]]:
        for film in pool:
            if film not in selected:
                selected.append(film)
                used_genres.update(film.get('genres', []))

    # Fill remaining 2 slots from combined pool, prioritising genre diversity
    remaining_pool = [c for c in scored if c not in selected]
    for film in remaining_pool:
        if len(selected) >= 6:
            break
        new_genres = set(film.get('genres', [])) - used_genres
        if new_genres or len(selected) < 5:
            selected.append(film)
            used_genres.update(film.get('genres', []))

    # Soft: try to include a pre-2000 film if not already present
    has_old = any((f.get('year') or 2000) < 2000 for f in selected)
    if not has_old:
        old_films = [c for c in remaining_pool if (c.get('year') or 2000) < 2000 and c not in selected]
        if old_films and len(selected) >= 6:
            # swap out the lowest-scored film in the last two slots
            selected[-1] = old_films[0]

    return selected[:6]
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_recommender.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/recommender.py tests/test_recommender.py
git commit -m "feat: recommender — scoring and diversity enforcement"
```

---

## Task 7: Gemini Client

**Files:**
- Create: `backend/gemini_client.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_gemini_client.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch, MagicMock
from gemini_client import generate_blurbs

TASTE_SUMMARY = 'Loves Drama, Mystery. Highly rated: Mulholland Drive, Persona.'

FILMS = [
    {'title': 'Inland Empire', 'year': 2006, 'director': 'David Lynch', 'genres': ['Drama']},
    {'title': 'The Seventh Seal', 'year': 1957, 'director': 'Ingmar Bergman', 'genres': ['Drama']},
]


def test_generate_blurbs_returns_dict_keyed_by_title():
    mock_response = MagicMock()
    mock_response.text = 'Inland Empire: You\'ll love this for its Lynchian surrealism.\nThe Seventh Seal: Perfect for fans of philosophical drama.'

    with patch('gemini_client.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = generate_blurbs(FILMS, TASTE_SUMMARY, api_key='fake')

    assert isinstance(result, dict)
    assert 'Inland Empire' in result
    assert 'The Seventh Seal' in result
    assert isinstance(result['Inland Empire'], str)
    assert len(result['Inland Empire']) > 5


def test_generate_blurbs_falls_back_on_api_error():
    with patch('gemini_client.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception('API error')
        mock_genai.GenerativeModel.return_value = mock_model

        result = generate_blurbs(FILMS, TASTE_SUMMARY, api_key='fake')

    # Should return fallback strings, not raise
    assert isinstance(result, dict)
    assert 'Inland Empire' in result
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_gemini_client.py -v
```

Expected: `ModuleNotFoundError: No module named 'gemini_client'`

- [ ] **Step 3: Implement gemini_client.py**

`backend/gemini_client.py`:
```python
import google.generativeai as genai


def generate_blurbs(films, taste_summary, api_key):
    """
    Generate a personalised "why you'd like it" blurb for each film.

    Returns dict keyed by film title.
    Falls back to a generic string if the API call fails.
    """
    film_list = '\n'.join(
        f"- {f['title']} ({f['year']}) directed by {f['director']}, genres: {', '.join(f.get('genres', []))}"
        for f in films
    )

    prompt = f"""You are recommending films to someone with this taste profile:
{taste_summary}

For each of the following films, write ONE sentence (max 20 words) explaining why this specific person would enjoy it. Reference films or directors from their taste profile where relevant. Reply with ONLY the film title followed by a colon and the sentence, one per line.

Films:
{film_list}"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return _parse_response(response.text, films)
    except Exception:
        return {f['title']: f"A highly regarded {f.get('genres', [''])[0].lower()} film worth watching." for f in films}


def _parse_response(text, films):
    """Parse Gemini response into a dict keyed by film title."""
    blurbs = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            title_part, _, blurb = line.partition(':')
            title = title_part.strip().strip('-').strip()
            blurbs[title] = blurb.strip()

    # Ensure every film has a blurb (fuzzy fallback)
    for film in films:
        if film['title'] not in blurbs:
            # Try case-insensitive match
            for key in blurbs:
                if key.lower() == film['title'].lower():
                    blurbs[film['title']] = blurbs[key]
                    break
            else:
                blurbs[film['title']] = f"A standout {film.get('genres', [''])[0].lower()} film."

    return blurbs
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_gemini_client.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/gemini_client.py tests/test_gemini_client.py
git commit -m "feat: gemini blurb generation"
```

---

## Task 8: Flask API Server

**Files:**
- Create: `backend/app.py`

- [ ] **Step 1: Write the failing test**

`tests/test_app.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch, MagicMock
import json

# Set env vars before importing app
os.environ['TMDB_READ_ACCESS_TOKEN'] = 'fake_tmdb'
os.environ['GEMINI_API_KEY'] = 'fake_gemini'

import app as flask_app

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


def make_test_client():
    flask_app.app.config['TESTING'] = True
    flask_app.app.config['DATA_DIR'] = FIXTURES
    return flask_app.app.test_client()


def mock_tmdb_get_movie(title, year):
    return {
        'tmdb_id': 1, 'title': title, 'year': year,
        'overview': 'A film.', 'poster_url': 'https://example.com/p.jpg',
        'tmdb_rating': 4.0, 'runtime': 120,
        'genres': ['Drama'], 'director': 'A Director', 'cast': ['Actor A'],
    }


def test_recommend_returns_200():
    client = make_test_client()
    with patch('app.TMDBClient') as MockTMDB, \
         patch('app.get_discovery_candidates', return_value=['Some Film', 'Another Film']), \
         patch('app.generate_blurbs', return_value={}):
        mock_instance = MagicMock()
        mock_instance.get_movie.side_effect = mock_tmdb_get_movie
        MockTMDB.return_value = mock_instance

        resp = client.get('/api/recommend')
    assert resp.status_code == 200


def test_recommend_returns_six_films():
    client = make_test_client()
    with patch('app.TMDBClient') as MockTMDB, \
         patch('app.get_discovery_candidates', return_value=[f'Film {i}' for i in range(20)]), \
         patch('app.generate_blurbs', return_value={f'Film {i}': 'Great pick.' for i in range(20)}):
        mock_instance = MagicMock()
        mock_instance.get_movie.side_effect = mock_tmdb_get_movie
        MockTMDB.return_value = mock_instance

        resp = client.get('/api/recommend')
        data = json.loads(resp.data)

    assert len(data['recommendations']) == 6


def test_recommend_response_shape():
    client = make_test_client()
    with patch('app.TMDBClient') as MockTMDB, \
         patch('app.get_discovery_candidates', return_value=[f'Film {i}' for i in range(20)]), \
         patch('app.generate_blurbs', return_value={f'Film {i}': 'A reason.' for i in range(20)}):
        mock_instance = MagicMock()
        mock_instance.get_movie.side_effect = mock_tmdb_get_movie
        MockTMDB.return_value = mock_instance

        resp = client.get('/api/recommend')
        data = json.loads(resp.data)

    film = data['recommendations'][0]
    for key in ['title', 'year', 'director', 'genres', 'poster_url', 'overview', 'why', 'source']:
        assert key in film, f"Missing key: {key}"


def test_stats_endpoint():
    client = make_test_client()
    resp = client.get('/api/stats')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'watched_count' in data
    assert 'watchlist_count' in data
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_app.py -v
```

Expected: `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: Implement app.py**

`backend/app.py`:
```python
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from letterboxd_parser import parse_ratings, parse_watchlist, get_watched_titles
from letterboxd_scraper import get_discovery_candidates
from taste_profile import build_profile
from recommender import pick_six
from tmdb_client import TMDBClient
from gemini_client import generate_blurbs

load_dotenv()

app = Flask(__name__)
CORS(app)

DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'data'))

# Session-level cache for scraped lists
_discovery_cache = None


def get_data_paths():
    data_dir = app.config.get('DATA_DIR', DATA_DIR)
    return {
        'ratings': os.path.join(data_dir, 'ratings.csv'),
        'watchlist': os.path.join(data_dir, 'watchlist.csv'),
    }


def get_tmdb():
    return TMDBClient(
        token=os.environ['TMDB_READ_ACCESS_TOKEN'],
        cache_path=os.path.join(os.path.dirname(__file__), '..', 'tmdb_cache.json'),
    )


@app.route('/api/recommend')
def recommend():
    global _discovery_cache

    paths = get_data_paths()
    tmdb = get_tmdb()

    ratings = parse_ratings(paths['ratings']) if os.path.exists(paths['ratings']) else []
    watchlist = parse_watchlist(paths['watchlist']) if os.path.exists(paths['watchlist']) else []
    watched = get_watched_titles(paths['ratings']) if os.path.exists(paths['ratings']) else set()

    # Build taste profile
    profile = build_profile(ratings, tmdb)

    # Build candidate pool
    if _discovery_cache is None:
        _discovery_cache = get_discovery_candidates()

    candidates = []

    for item in watchlist:
        if item['title'].lower() in watched:
            continue
        data = tmdb.get_movie(item['title'], item['year'])
        if data:
            candidates.append({**data, 'source': 'watchlist'})

    for title in _discovery_cache:
        if title.lower() in watched:
            continue
        if any(c['title'].lower() == title.lower() for c in candidates):
            continue
        data = tmdb.get_movie(title, None)
        if data:
            candidates.append({**data, 'source': 'discovered'})

    if len(candidates) < 6:
        return jsonify({'error': 'Not enough candidates. Add more CSV data or check your data/ folder.'}), 422

    picks = pick_six(candidates, profile)

    # Generate Gemini blurbs
    blurbs = generate_blurbs(picks, profile['summary'], api_key=os.environ['GEMINI_API_KEY'])
    for film in picks:
        film['why'] = blurbs.get(film['title'], '')

    return jsonify({
        'recommendations': picks,
        'taste_summary': profile['summary'],
    })


@app.route('/api/stats')
def stats():
    paths = get_data_paths()
    watched_count = 0
    watchlist_count = 0

    if os.path.exists(paths['ratings']):
        watched_count = len(get_watched_titles(paths['ratings']))
    if os.path.exists(paths['watchlist']):
        watchlist_count = len(parse_watchlist(paths['watchlist']))

    return jsonify({
        'watched_count': watched_count,
        'watchlist_count': watchlist_count,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

- [ ] **Step 4: Run all backend tests**

```bash
pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app.py tests/test_app.py
git commit -m "feat: flask API server with /api/recommend and /api/stats"
```

---

## Task 9: React + Vite Frontend Scaffolding

**Files:**
- Create: `frontend/` (via Vite)
- Create: `frontend/vite.config.js`

- [ ] **Step 1: Scaffold the React project**

```bash
cd /path/to/movie_recommender
npm create vite@latest frontend -- --template react
cd frontend && npm install
npm install axios
```

Expected: `frontend/` created with `src/`, `package.json`, etc.

- [ ] **Step 2: Replace vite.config.js with API proxy**

`frontend/vite.config.js`:
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
})
```

- [ ] **Step 3: Clear boilerplate**

Delete `frontend/src/App.css` and `frontend/src/assets/react.svg` and `frontend/public/vite.svg`.

```bash
rm frontend/src/App.css frontend/src/assets/react.svg frontend/public/vite.svg
```

- [ ] **Step 4: Verify dev server starts**

```bash
# Make sure backend is running: cd backend && python app.py
cd frontend && npm run dev
```

Expected: Vite dev server starts on `http://localhost:5173`. Browser shows default React page (we'll replace it in upcoming tasks).

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "chore: react + vite frontend scaffold with API proxy"
```

---

## Task 10: Deep Space CSS — Global Styles

**Files:**
- Create: `frontend/src/index.css`

- [ ] **Step 1: Replace index.css with Deep Space theme**

`frontend/src/index.css`:
```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --bg: #07071a;
  --surface: rgba(255, 255, 255, 0.06);
  --border: rgba(255, 255, 255, 0.12);
  --accent: #7c3aed;
  --accent-glow: rgba(124, 58, 237, 0.4);
  --text: #ffffff;
  --text-muted: rgba(255, 255, 255, 0.45);
  --text-dim: rgba(255, 255, 255, 0.25);
  --purple-soft: rgba(180, 140, 255, 0.8);
  --radius-card: 16px;
  --radius-pill: 50px;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Ambient background blobs */
.bg-blobs {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-blobs .blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: blob-drift 14s ease-in-out infinite alternate;
}

.bg-blobs .blob-1 {
  width: 600px; height: 600px;
  background: #5b21b6;
  top: -150px; left: -150px;
  animation-delay: 0s;
}

.bg-blobs .blob-2 {
  width: 450px; height: 450px;
  background: #1e3a8a;
  top: 25%; right: -100px;
  animation-delay: -5s;
}

.bg-blobs .blob-3 {
  width: 400px; height: 400px;
  background: #4c1d95;
  bottom: -100px; left: 35%;
  animation-delay: -10s;
}

@keyframes blob-drift {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(25px, 20px) scale(1.06); }
}

/* Glass utility */
.glass {
  background: var(--surface);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
  border: 1px solid var(--border);
}

/* App shell */
.app {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px 56px;
}

/* Section label */
.section-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-dim);
  margin-bottom: 14px;
}

/* Genre chip */
.genre-chip {
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* Source tag */
.source-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(124, 58, 237, 0.18);
  border: 1px solid rgba(124, 58, 237, 0.35);
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 0.68rem;
  color: var(--purple-soft);
  margin-bottom: 10px;
}

.source-tag .dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #a78bfa;
  flex-shrink: 0;
}

/* Card flip animation */
.flip-container {
  perspective: 1000px;
}

.flip-inner {
  position: relative;
  width: 100%; height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.flip-inner.is-flipping {
  transform: rotateY(180deg);
}

.flip-front,
.flip-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.flip-back {
  transform: rotateY(180deg);
}
```

- [ ] **Step 2: Verify the CSS loads**

Open `http://localhost:5173` — background should be near-black. No errors in console.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/index.css
git commit -m "feat: deep space CSS theme with glass utilities and blob animation"
```

---

## Task 11: HeroCard Component

**Files:**
- Create: `frontend/src/components/HeroCard.jsx`

- [ ] **Step 1: Create HeroCard.jsx**

`frontend/src/components/HeroCard.jsx`:
```jsx
export default function HeroCard({ film, isFlipping }) {
  if (!film) return null

  return (
    <div className="flip-container" style={{ marginBottom: '20px' }}>
      <div className={`flip-inner ${isFlipping ? 'is-flipping' : ''}`}>
        {/* Front — shown normally */}
        <div className="flip-front">
          <HeroCardInner film={film} />
        </div>
        {/* Back — shown mid-flip (same content, resolves after flip) */}
        <div className="flip-back">
          <HeroCardInner film={film} />
        </div>
      </div>
    </div>
  )
}

function HeroCardInner({ film }) {
  return (
    <div className="glass hero-card">
      <div className="hero-poster">
        {film.poster_url ? (
          <img src={film.poster_url} alt={film.title} />
        ) : (
          <div className="poster-placeholder">🎬</div>
        )}
      </div>
      <div className="hero-body">
        <div>
          <div className="source-tag">
            <span className="dot" />
            {film.source === 'watchlist' ? 'From your watchlist' : 'Discovered for you'}
          </div>
          <h2 className="hero-title">{film.title}</h2>
          <div className="hero-meta">
            <span>{film.year}</span>
            <span>{film.director}</span>
            {film.runtime && <span>{film.runtime} min</span>}
            {film.tmdb_rating > 0 && <span>★ {film.tmdb_rating}</span>}
          </div>
          <p className="hero-description">{film.overview}</p>
          {film.why && (
            <div className="why-tag">
              <span className="why-icon">✦</span>
              <span>{film.why}</span>
            </div>
          )}
        </div>
        <div className="hero-genres">
          {(film.genres || []).map(g => (
            <span key={g} className="genre-chip">{g}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Add HeroCard styles to index.css**

Append to `frontend/src/index.css`:
```css
/* ── HeroCard ── */
.hero-card {
  border-radius: var(--radius-card);
  overflow: hidden;
  display: flex;
  height: 300px;
}

.hero-poster {
  width: 200px;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
}

.hero-poster img {
  width: 100%; height: 100%;
  object-fit: cover;
}

.hero-poster::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(to right, transparent 60%, var(--bg) 100%);
}

.poster-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: rgba(124, 58, 237, 0.15);
  font-size: 2rem; opacity: 0.5;
}

.hero-body {
  flex: 1;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-left: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.03);
}

.hero-title {
  font-size: 1.7rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.15;
  margin-bottom: 6px;
}

.hero-meta {
  display: flex;
  gap: 10px;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 14px;
}

.hero-meta span::after { content: '·'; margin-left: 10px; }
.hero-meta span:last-child::after { content: ''; }

.hero-description {
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.6;
  margin-bottom: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.why-tag {
  display: inline-flex;
  align-items: flex-start;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

.why-icon { opacity: 0.5; flex-shrink: 0; margin-top: 1px; }

.hero-genres {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/HeroCard.jsx frontend/src/index.css
git commit -m "feat: HeroCard component with flip support"
```

---

## Task 12: MovieCard Component

**Files:**
- Create: `frontend/src/components/MovieCard.jsx`

- [ ] **Step 1: Create MovieCard.jsx**

`frontend/src/components/MovieCard.jsx`:
```jsx
export default function MovieCard({ film, isFlipping, onClick }) {
  return (
    <div
      className="flip-container movie-card-wrapper"
      onClick={() => onClick && onClick(film)}
    >
      <div className={`flip-inner ${isFlipping ? 'is-flipping' : ''}`}>
        <div className="flip-front">
          <MovieCardInner film={film} />
        </div>
        <div className="flip-back">
          <MovieCardInner film={film} />
        </div>
      </div>
    </div>
  )
}

function MovieCardInner({ film }) {
  return (
    <div className="glass movie-card">
      <div className="movie-poster">
        {film.poster_url ? (
          <img src={film.poster_url} alt={film.title} />
        ) : (
          <div className="poster-placeholder" style={{ fontSize: '1.2rem' }}>🎬</div>
        )}
      </div>
      <div className="movie-body">
        <div className="movie-title">{film.title}</div>
        <div className="movie-year">{film.year} · {film.director}</div>
        {film.why && <div className="movie-why">{film.why}</div>}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Add MovieCard styles to index.css**

Append to `frontend/src/index.css`:
```css
/* ── MovieCard ── */
.movie-card-wrapper {
  cursor: pointer;
}

.movie-card {
  border-radius: var(--radius-card);
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  height: 100%;
}

.movie-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 40px var(--accent-glow);
}

.movie-poster {
  width: 100%;
  aspect-ratio: 2 / 3;
  overflow: hidden;
}

.movie-poster img {
  width: 100%; height: 100%;
  object-fit: cover;
}

.movie-body {
  padding: 10px 10px 12px;
}

.movie-title {
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 3px;
}

.movie-year {
  font-size: 0.7rem;
  color: var(--text-dim);
}

.movie-why {
  font-size: 0.68rem;
  color: var(--purple-soft);
  margin-top: 5px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MovieCard.jsx frontend/src/index.css
git commit -m "feat: MovieCard component with hover lift and flip support"
```

---

## Task 13: ShuffleButton Component

**Files:**
- Create: `frontend/src/components/ShuffleButton.jsx`

- [ ] **Step 1: Create ShuffleButton.jsx**

`frontend/src/components/ShuffleButton.jsx`:
```jsx
export default function ShuffleButton({ onClick, loading }) {
  return (
    <div className="shuffle-wrap">
      <button
        className={`shuffle-btn ${loading ? 'loading' : ''}`}
        onClick={onClick}
        disabled={loading}
      >
        <span className={`shuffle-icon ${loading ? 'spinning' : ''}`}>⟳</span>
        {loading ? 'Finding picks…' : 'Shuffle Recommendations'}
      </button>
      {!loading && (
        <p className="shuffle-hint">Cards flip to reveal new picks</p>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Add ShuffleButton styles to index.css**

Append to `frontend/src/index.css`:
```css
/* ── ShuffleButton ── */
.shuffle-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.shuffle-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.35), rgba(59, 130, 246, 0.25));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(124, 58, 237, 0.5);
  border-radius: var(--radius-pill);
  padding: 14px 36px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text);
  cursor: pointer;
  box-shadow: 0 0 30px var(--accent-glow), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
  letter-spacing: 0.01em;
}

.shuffle-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.55), rgba(59, 130, 246, 0.4));
  box-shadow: 0 0 50px var(--accent-glow), inset 0 1px 0 rgba(255, 255, 255, 0.15);
  transform: scale(1.03);
}

.shuffle-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.shuffle-icon {
  font-size: 1.1rem;
  display: inline-block;
}

.shuffle-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.shuffle-hint {
  font-size: 0.72rem;
  color: var(--text-dim);
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ShuffleButton.jsx frontend/src/index.css
git commit -m "feat: ShuffleButton with loading and spin states"
```

---

## Task 14: App.jsx — Wire Everything Together

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/main.jsx`

- [ ] **Step 1: Replace main.jsx**

`frontend/src/main.jsx`:
```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 2: Write App.jsx**

`frontend/src/App.jsx`:
```jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import HeroCard from './components/HeroCard.jsx'
import MovieCard from './components/MovieCard.jsx'
import ShuffleButton from './components/ShuffleButton.jsx'

const FLIP_DURATION = 600   // ms — matches CSS transition
const FLIP_STAGGER  = 120   // ms between card flips

export default function App() {
  const [films, setFilms]         = useState([])
  const [stats, setStats]         = useState(null)
  const [loading, setLoading]     = useState(false)
  const [flipping, setFlipping]   = useState([]) // indices currently flipping
  const [heroIndex, setHeroIndex] = useState(0)
  const [error, setError]         = useState(null)

  useEffect(() => {
    fetchStats()
    fetchRecommendations()
  }, [])

  async function fetchStats() {
    try {
      const { data } = await axios.get('/api/stats')
      setStats(data)
    } catch {
      // stats are decorative — silent fail
    }
  }

  async function fetchRecommendations() {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.get('/api/recommend')
      await runFlipAnimation(data.recommendations.length)
      setFilms(data.recommendations)
      setHeroIndex(0)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not load recommendations. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  async function runFlipAnimation(count) {
    // Stagger flip-in across all cards
    for (let i = 0; i < count; i++) {
      setTimeout(() => {
        setFlipping(prev => [...prev, i])
        setTimeout(() => {
          setFlipping(prev => prev.filter(x => x !== i))
        }, FLIP_DURATION)
      }, i * FLIP_STAGGER)
    }
    // Wait for all flips to complete before updating films
    await new Promise(resolve => setTimeout(resolve, count * FLIP_STAGGER + FLIP_DURATION))
  }

  const hero = films[heroIndex] || null
  const row  = films.filter((_, i) => i !== heroIndex)

  return (
    <>
      <div className="bg-blobs">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
        <div className="blob blob-3" />
      </div>

      <div className="app">
        {/* Header */}
        <header className="app-header">
          <div className="header-left">
            <div className="avatar">H</div>
            <div>
              <h1 className="app-title">What to Watch</h1>
              <p className="app-sub">hafsahnasir · Letterboxd</p>
            </div>
          </div>
          {stats && (
            <div className="header-stats">
              <span>{stats.watched_count} films watched</span>
              <span className="stats-watchlist">{stats.watchlist_count} in watchlist</span>
            </div>
          )}
        </header>

        {error ? (
          <div className="error-box glass">{error}</div>
        ) : (
          <>
            {/* Hero */}
            <p className="section-label">Tonight's Pick</p>
            <HeroCard film={hero} isFlipping={flipping.includes(heroIndex)} />

            {/* Row of 5 */}
            <div className="row-header">
              <p className="section-label" style={{ marginBottom: 0 }}>More Picks</p>
            </div>
            <div className="cards-row">
              {row.map((film, i) => (
                <MovieCard
                  key={film.tmdb_id}
                  film={film}
                  isFlipping={flipping.includes(i + (i >= heroIndex ? 1 : 0))}
                  onClick={() => setHeroIndex(films.indexOf(film))}
                />
              ))}
            </div>
          </>
        )}

        {/* Shuffle */}
        <ShuffleButton onClick={fetchRecommendations} loading={loading} />
      </div>
    </>
  )
}
```

- [ ] **Step 3: Add App-level styles to index.css**

Append to `frontend/src/index.css`:
```css
/* ── App shell ── */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #3b82f6);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.app-title {
  font-size: 1.15rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.app-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 1px;
}

.header-stats {
  text-align: right;
  font-size: 0.75rem;
  color: var(--text-dim);
  line-height: 1.6;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stats-watchlist { color: var(--purple-soft); }

.row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.cards-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 36px;
}

.error-box {
  border-radius: var(--radius-card);
  padding: 24px;
  color: rgba(255, 180, 180, 0.9);
  margin-bottom: 32px;
  font-size: 0.9rem;
  line-height: 1.6;
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.jsx frontend/src/main.jsx frontend/src/index.css
git commit -m "feat: App.jsx — wires all components, shuffle animation, hero swap"
```

---

## Task 15: End-to-End Smoke Test

- [ ] **Step 1: Export your Letterboxd data**

In Letterboxd: **Settings → Import & Export → Export Your Data**. Download the zip. Extract `ratings.csv`, `watchlist.csv`, `watched.csv` into `data/`.

- [ ] **Step 2: Start the backend**

```bash
cd backend && python app.py
```

Expected: `Running on http://127.0.0.1:5000`

- [ ] **Step 3: Curl the stats endpoint**

```bash
curl http://localhost:5000/api/stats
```

Expected: `{"watched_count": <number>, "watchlist_count": <number>}` — real counts from your CSV.

- [ ] **Step 4: Start the frontend**

```bash
cd frontend && npm run dev
```

Open **http://localhost:5173**.

Expected: App loads with header showing real watch count, 6 film cards render with real TMDB posters.

- [ ] **Step 5: Verify recommendations quality**

- Hero card shows a full poster, title, director, description, and "why you'd like it" text
- Row of 5 shows posters + short blurbs
- At least 1 card shows "From your watchlist" tag
- Click Shuffle — all 6 cards flip, new films appear

- [ ] **Step 6: Verify genre diversity**

Across the 6 recommendations, at least 3 different genres should appear.

- [ ] **Step 7: Final commit**

```bash
git add .
git commit -m "feat: complete movie recommender — end-to-end working"
```
