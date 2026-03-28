import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch
from letterboxd_scraper import scrape_list, get_discovery_candidates

SAMPLE_HTML = """
<html><body>
<ul class="poster-list">
  <li class="poster-container">
    <div class="film-poster" data-film-slug="mulholland-drive"
         data-film-id="1018" data-target-link="/film/mulholland-drive/">
      <img alt="Mulholland Drive" />
    </div>
  </li>
  <li class="poster-container">
    <div class="film-poster" data-film-slug="chungking-express"
         data-film-id="11776" data-target-link="/film/chungking-express/">
      <img alt="Chungking Express" />
    </div>
  </li>
</ul>
</body></html>
"""


def test_scrape_list_returns_titles():
    with patch('letterboxd_scraper.requests.get') as mock_get:
        mock_get.return_value.text = SAMPLE_HTML
        mock_get.return_value.raise_for_status = lambda: None
        results = scrape_list('https://letterboxd.com/films/')
    assert 'Mulholland Drive' in results
    assert 'Chungking Express' in results


def test_scrape_list_returns_list_of_strings():
    with patch('letterboxd_scraper.requests.get') as mock_get:
        mock_get.return_value.text = SAMPLE_HTML
        mock_get.return_value.raise_for_status = lambda: None
        results = scrape_list('https://letterboxd.com/films/')
    assert isinstance(results, list)
    assert all(isinstance(t, str) for t in results)


def test_get_discovery_candidates_deduplicates():
    with patch('letterboxd_scraper.scrape_list', return_value=['Film A', 'Film A', 'Film B']):
        results = get_discovery_candidates()
    assert results.count('Film A') == 1
