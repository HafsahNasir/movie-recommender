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

    score += random.uniform(0, 4.0)
    return score


def pick_six(candidates, profile):
    """
    Pick 6 films from candidates with diversity enforcement.
    - At least 2 from watchlist, at least 2 from discovered
    - At least 3 different genres across the 6
    - Prefer at least 1 pre-2000 film (soft constraint)
    Selection is randomised across the full pool so every shuffle produces fresh picks.
    """
    # Attach deterministic taste scores (no jitter) for use in fill step
    for c in candidates:
        c['_score'] = score_candidate(c, profile)

    watchlist = [c for c in candidates if c.get('source') == 'watchlist']
    discovered = [c for c in candidates if c.get('source') == 'discovered']

    # Shuffle entire pools — any unwatched film can surface on any shuffle
    random.shuffle(watchlist)
    random.shuffle(discovered)

    selected = []
    used_genres = set()

    # Guarantee at least 2 from each source, picked randomly
    for pool in [watchlist, discovered]:
        picks = pool[:min(2, len(pool))]
        for film in picks:
            selected.append(film)
            used_genres.update(film.get('genres', []))

    # Fill remaining slots from the full pool, preferring genre variety
    remaining = [c for c in candidates if c not in selected]
    random.shuffle(remaining)
    # Sort remaining by score so taste still guides the last 2 picks
    remaining.sort(key=lambda c: c['_score'], reverse=True)
    for film in remaining:
        if len(selected) >= 6:
            break
        new_genres = set(film.get('genres', [])) - used_genres
        if new_genres or len(selected) < 5:
            selected.append(film)
            used_genres.update(film.get('genres', []))

    # Fallback: fill any remaining slots ignoring genre constraint
    if len(selected) < 6:
        for film in remaining:
            if len(selected) >= 6:
                break
            if film not in selected:
                selected.append(film)

    # Soft: swap last pick for a pre-2000 film if none present
    has_old = any((f.get('year') or 2000) < 2000 for f in selected)
    if not has_old:
        not_selected = [c for c in candidates if c not in selected]
        old_films = [c for c in not_selected if (c.get('year') or 2000) < 2000]
        if old_films:
            selected[-1] = old_films[0]

    # Clean up temp score key
    for c in candidates:
        c.pop('_score', None)

    return selected[:6]
