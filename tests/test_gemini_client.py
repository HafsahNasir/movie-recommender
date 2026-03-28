import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch, MagicMock
from gemini_client import generate_blurbs

TASTE_SUMMARY = 'Loves Drama, Mystery. Highly rated: Mulholland Drive, Persona.'

FILMS = [
    {'title': 'Inland Empire', 'year': 2006, 'director': 'David Lynch', 'genres': ['Drama']},
    {'title': 'The Seventh Seal', 'year': 1957, 'director': 'Ingmar Bergman', 'genres': ['Drama']},
]


def test_generate_blurbs_returns_dict_keyed_by_title():
    mock_response = MagicMock()
    mock_response.text = "Inland Empire: You'll love this for its Lynchian surrealism.\nThe Seventh Seal: Perfect for fans of philosophical drama."

    with patch('gemini_client.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = generate_blurbs(FILMS, TASTE_SUMMARY, api_key='fake')

    assert isinstance(result, dict)
    assert 'Inland Empire' in result
    assert 'The Seventh Seal' in result
    assert isinstance(result['Inland Empire'], str)
    assert len(result['Inland Empire']) > 5


def test_generate_blurbs_falls_back_on_api_error():
    with patch('gemini_client.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception('API error')
        mock_genai.GenerativeModel.return_value = mock_model

        result = generate_blurbs(FILMS, TASTE_SUMMARY, api_key='fake')

    assert isinstance(result, dict)
    assert 'Inland Empire' in result
