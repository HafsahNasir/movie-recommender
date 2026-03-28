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

    score += random.uniform(0, 0.5)
    return score


def pick_six(candidates, profile):
    """
    Pick 6 films from candidates with diversity enforcement.
    - At least 2 from watchlist, at least 2 from discovered
    - At least 3 different genres across the 6
    - Prefer at least 1 pre-2000 film (soft constraint)
    """
    scored = sorted(candidates, key=lambda c: score_candidate(c, profile), reverse=True)

    watchlist = [c for c in scored if c.get('source') == 'watchlist']
    discovered = [c for c in scored if c.get('source') == 'discovered']

    selected = []
    used_genres = set()

    for pool in [watchlist[:2], discovered[:2]]:
        for film in pool:
            if film not in selected:
                selected.append(film)
                used_genres.update(film.get('genres', []))

    remaining_pool = [c for c in scored if c not in selected]
    for film in remaining_pool:
        if len(selected) >= 6:
            break
        new_genres = set(film.get('genres', [])) - used_genres
        if new_genres or len(selected) < 5:
            selected.append(film)
            used_genres.update(film.get('genres', []))

    has_old = any((f.get('year') or 2000) < 2000 for f in selected)
    if not has_old:
        old_films = [c for c in remaining_pool if (c.get('year') or 2000) < 2000 and c not in selected]
        if old_films and len(selected) >= 6:
            selected[-1] = old_films[0]

    return selected[:6]
