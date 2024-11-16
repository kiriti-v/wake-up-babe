# tests/test_main.py

import unittest
from unittest.mock import patch, MagicMock
from main import get_date_range, main

class TestMain(unittest.TestCase):
    @patch('main.TMDBCollector')
    @patch('main.IGDBCollector')
    @patch('main.ExcitementScoreCalculator')
    def test_main_flow(self, mock_calculator, mock_igdb, mock_tmdb):
        # Mock collectors
        mock_tmdb_instance = MagicMock()
        mock_tmdb_instance.get_releases.return_value = [
            {'title': 'Test Movie', 'type': 'movie', 'release_date': '2024-01-01', 'popularity': 90}
        ]
        mock_tmdb.return_value = mock_tmdb_instance

        mock_igdb_instance = MagicMock()
        mock_igdb_instance.get_releases.return_value = [
            {'title': 'Test Game', 'type': 'game', 'release_date': '2024-01-02', 'popularity': 95}
        ]
        mock_igdb.return_value = mock_igdb_instance

        # Mock calculator
        mock_calculator_instance = MagicMock()
        mock_calculator_instance.calculate_score.return_value = 85
        mock_calculator.return_value = mock_calculator_instance

        # Run main function
        with patch('builtins.print') as mock_print:
            main()

        # Assert that print was called (indicating results were displayed)
        mock_print.assert_called()

    def test_get_date_range(self):
        start_date, end_date = get_date_range(7)
        self.assertIsInstance(start_date, str)
        self.assertIsInstance(end_date, str)
        # Add more specific checks if needed

if __name__ == '__main__':
    unittest.main()