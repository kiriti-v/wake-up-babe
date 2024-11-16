import unittest
from unittest.mock import patch, MagicMock
from collectors.igdb_collector import IGDBCollector
from datetime import datetime

class TestIGDBCollector(unittest.TestCase):
    def setUp(self):
        self.collector = IGDBCollector(client_id='dummy_id', client_secret='dummy_secret')

    @patch('collectors.igdb_collector.requests.post')
    def test_get_access_token(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'dummy_token'}
        mock_post.return_value = mock_response

        self.collector._get_access_token()
        self.assertEqual(self.collector.access_token, 'dummy_token')

    @patch('collectors.igdb_collector.requests.post')
    def test_get_releases_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Test Game',
                'release_dates': [{'date': int(datetime.now().timestamp())}],
                'popularity': 100
            }
        ]
        mock_post.return_value = mock_response

        self.collector.access_token = 'dummy_token'  # Set token manually for test
        start_date = '2024-01-01'
        end_date = '2024-01-07'
        releases = self.collector.get_releases(start_date, end_date)

        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]['title'], 'Test Game')
        self.assertEqual(releases[0]['type'], 'game')

    @patch('collectors.igdb_collector.requests.post')
    def test_get_releases_error(self, mock_post):
        mock_post.side_effect = Exception('API Error')

        self.collector.access_token = 'dummy_token'  # Set token manually for test
        start_date = '2024-01-01'
        end_date = '2024-01-07'
        releases = self.collector.get_releases(start_date, end_date)

        self.assertEqual(len(releases), 0)

    def test_format_release(self):
        game_data = {
            'id': 1,
            'name': 'Test Game',
            'release_dates': [{'date': int(datetime.now().timestamp())}],
            'popularity': 100
        }
        formatted = self.collector._format_release(game_data)

        self.assertEqual(formatted['title'], 'Test Game')
        self.assertEqual(formatted['type'], 'game')
        self.assertIsNotNone(formatted['release_date'])
        self.assertEqual(formatted['popularity'], 100)

if __name__ == '__main__':
    unittest.main()