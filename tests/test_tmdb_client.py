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
