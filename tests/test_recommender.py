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
