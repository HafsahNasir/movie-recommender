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
            if rating >= min_rating:
                results.append({
                    'title': row['Name'].strip(),
                    'year': int(row['Year']) if row['Year'] else None,
                    'rating': rating,
                })
    return results


def parse_watchlist(path):
    """Return list of {title, year} from watchlist.csv."""
    results = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            results.append({
                'title': row['Name'].strip(),
                'year': int(row['Year']) if row['Year'] else None,
            })
    return results


def get_watched_titles(ratings_path):
    """Return set of all watched film titles (lowercased for comparison)."""
    titles = set()
    with open(ratings_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            titles.add(row['Name'].strip().lower())
    return titles
