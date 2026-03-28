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
            try:
                year = int(row['Year']) if row['Year'] else None
            except ValueError:
                year = None
            if rating >= min_rating:
                results.append({
                    'title': row['Name'].strip(),
                    'year': year,
                    'rating': rating,
                })
    return results


def parse_watchlist(path):
    """Return list of {title, year} from watchlist.csv."""
    results = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                year = int(row['Year']) if row['Year'] else None
            except ValueError:
                year = None
            results.append({
                'title': row['Name'].strip(),
                'year': year,
            })
    return results


def get_watched_titles(ratings_path, watched_path=None):
    """Return set of all watched film titles (lowercased for comparison).
    Reads from ratings.csv and optionally watched.csv for full coverage."""
    titles = set()
    for path in filter(None, [ratings_path, watched_path]):
        try:
            with open(path, newline='', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    titles.add(row['Name'].strip().lower())
        except FileNotFoundError:
            pass
    return titles
