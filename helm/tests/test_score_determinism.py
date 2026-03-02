import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.validation.validator import Validator

class ScoreDeterminismTests(unittest.TestCase):
    def setUp(self):
        self.validator = Validator()
        self.input = {
            'revenue': 1000,
            'costs': 400,
            'investment': 200,
            'expected_returns': 1200,
            'confidence': 0.85,
            'roi': 1.5
        }
        self.required = ['revenue', 'costs', 'investment', 'expected_returns']

    def test_same_input_same_score(self):
        scores = []
        for _ in range(10):
            score = self.validator.calculate_validation_score(self.input, self.required)
            scores.append(score.weighted_score)
        self.assertTrue(all(s == scores[0] for s in scores))

if __name__ == '__main__':
    unittest.main()
