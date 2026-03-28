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

    profile = build_profile(ratings, tmdb)

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
