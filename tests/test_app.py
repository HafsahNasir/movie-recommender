import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch, MagicMock
import json

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
    flask_app._discovery_cache = None
    client = make_test_client()
    with patch('app.TMDBClient') as MockTMDB, \
         patch('app.get_discovery_candidates', return_value=[f'Film {i}' for i in range(10)]), \
         patch('app.generate_blurbs', return_value={}):
        mock_instance = MagicMock()
        mock_instance.get_movie.side_effect = mock_tmdb_get_movie
        MockTMDB.return_value = mock_instance

        resp = client.get('/api/recommend')
    assert resp.status_code == 200


def test_recommend_returns_six_films():
    flask_app._discovery_cache = None
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
    flask_app._discovery_cache = None
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
