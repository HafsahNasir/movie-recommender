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
    assert 'mulholland drive' in watched
    assert 'avengers: endgame' in watched


def test_get_watched_titles_returns_set():
    watched = get_watched_titles(os.path.join(FIXTURES, 'ratings.csv'))
    assert isinstance(watched, set)
