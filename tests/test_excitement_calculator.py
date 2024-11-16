# tests/test_excitement_calculator.py

import unittest
from calculators.excitement_calculator import ExcitementScoreCalculator

class TestExcitementScoreCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = ExcitementScoreCalculator()

    def test_calculate_score(self):
        release = {
            'title': 'Test Release',
            'type': 'movie',
            'popularity': 80
        }
        score = self.calculator.calculate_score(release)
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_calculate_score_max_popularity(self):
        release = {
            'title': 'Very Popular Release',
            'type': 'movie',
            'popularity': 150  # Above 100
        }
        score = self.calculator.calculate_score(release)
        self.assertLessEqual(score, 100)

    def test_calculate_score_no_popularity(self):
        release = {
            'title': 'Unknown Release',
            'type': 'movie'
        }
        score = self.calculator.calculate_score(release)
        self.assertEqual(score, 0)  # Expect 0 when popularity is not present

if __name__ == '__main__':
    unittest.main()
