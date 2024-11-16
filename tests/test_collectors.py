import unittest
from unittest.mock import patch, MagicMock
from collectors.igdb_collector import IGDBCollector
import requests

class TestIGDBCollectorWithCache(unittest.TestCase):
    def setUp(self):
        self.collector = IGDBCollector(client_id='dummy_id', client_secret='dummy_secret')
        self.cache = {}

    @patch('collectors.igdb_collector.requests.post')
    def test_token_refresh(self, mock_post):
        # Mock responses
        initial_access_token_response = MagicMock()
        initial_access_token_response.status_code = 200
        initial_access_token_response.json.return_value = {'access_token': 'dummy_token'}

        expired_token_response = MagicMock()
        expired_token_response.status_code = 401
        expired_token_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error: Unauthorized")

        new_access_token_response = MagicMock()
        new_access_token_response.status_code = 200
        new_access_token_response.json.return_value = {'access_token': 'new_dummy_token'}

        release_dates_response = MagicMock()
        release_dates_response.status_code = 200
        release_dates_response.json.return_value = [
            {
                'id': 1,
                'game': 1001,
                'date': 1704067200  # Sample timestamp
            }
        ]

        game_data_response = MagicMock()
        game_data_response.status_code = 200
        game_data_response.json.return_value = [
            {
                'id': 1001,
                'name': 'Test Game',
                'popularity': 100
            }
        ]

        # Configure side_effect with response sequence
        mock_post.side_effect = [
            initial_access_token_response,  # Initial token fetch
            expired_token_response,         # Attempt to fetch release dates with expired token
            new_access_token_response,      # Fetch new token
            release_dates_response,         # Fetch release dates with new token
            game_data_response              # Fetch game data
        ]

        # Invoke method
        releases = self.collector.get_releases('2024-01-01', '2024-01-07', self.cache)

        # Assertions
        self.assertEqual(len(releases), 1)
        self.assertEqual(mock_post.call_count, 5)
        self.assertEqual(self.collector.access_token, 'new_dummy_token')
        self.assertEqual(releases[0]['title'], 'Test Game')

if __name__ == '__main__':
    unittest.main()
