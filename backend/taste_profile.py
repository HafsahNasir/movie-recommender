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

    Returns dict with: genres (Counter), directors (Counter), actors (Counter),
    eras (Counter), high_rated_titles (list), summary (str)
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
