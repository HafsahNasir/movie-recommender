import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import MagicMock
from taste_profile import build_profile

def make_tmdb(genre_map):
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
        {'title': 'Film C', 'year': 2010, 'rating': 2.0},
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
