# tests/test_tmdb_collector.py

import unittest
from unittest.mock import patch, MagicMock
from collectors.tmdb_collector import TMDBCollector
from datetime import datetime, timedelta

class TestTMDBCollector(unittest.TestCase):
    def setUp(self):
        self.collector = TMDBCollector(api_key='dummy_key')

    @patch('collectors.tmdb_collector.requests.get')
    def test_get_releases_success(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 1,
                    'title': 'Test Movie',
                    'release_date': '2024-01-01',
                    'popularity': 100
                }
            ]
        }
        mock_get.return_value = mock_response

        start_date = '2024-01-01'
        end_date = '2024-01-07'
        releases = self.collector.get_releases('movie', start_date, end_date)

        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]['title'], 'Test Movie')
        self.assertEqual(releases[0]['type'], 'movie')

    @patch('collectors.tmdb_collector.requests.get')
    def test_get_releases_error(self, mock_get):
        # Mock API error
        mock_get.side_effect = Exception('API Error')

        start_date = '2024-01-01'
        end_date = '2024-01-07'
        releases = self.collector.get_releases('movie', start_date, end_date)

        self.assertEqual(len(releases), 0)

    def test_format_release(self):
        movie_data = {
            'id': 1,
            'title': 'Test Movie',
            'release_date': '2024-01-01',
            'popularity': 100
        }
        formatted = self.collector._format_release(movie_data, 'movie')

        self.assertEqual(formatted['title'], 'Test Movie')
        self.assertEqual(formatted['type'], 'movie')
        self.assertEqual(formatted['release_date'], '2024-01-01')
        self.assertEqual(formatted['popularity'], 100)

if __name__ == '__main__':
    unittest.main()
