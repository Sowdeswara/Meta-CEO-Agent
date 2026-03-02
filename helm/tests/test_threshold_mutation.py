import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.agents.head_agent import HeadAgent
from helm.validation.validator import Validator
from helm.config import Config


class ThresholdMutationTests(unittest.TestCase):
    def setUp(self):
        config = Config()
        config.DEVELOPMENT_MODE = True
        self.head = HeadAgent(config=config, validator=Validator(config))

        # simple context identical each time
        self.ctx = {
            'user_id': 'u',
            'session_id': 's',
            'revenue': 100,
            'costs': 50,
            'investment': 10,
            'expected_returns': 200,
            'timeframe_years': 1,
            'confidence': 0.9,
            'roi': 19.0
        }
        self.required = ['revenue', 'costs', 'investment', 'expected_returns']

    def test_threshold_change(self):
        # baseline with default threshold 0.70
        from helm.schemas import DecisionInput
        di = DecisionInput(prompt='x', context=self.ctx, user_id='u', session_id='s', required_fields=self.required)
        out1 = self.head.process(di).to_dict()
        score = out1['validation_score']
        self.assertEqual(score, out1['validation_score'])
        self.assertTrue(score >= 0)  # sanity

        # mutate threshold to above score and re-run
        self.head.config.validation_threshold = min(score + 0.1, 1.0)
        di2 = DecisionInput(prompt='x', context=self.ctx, user_id='u', session_id='s', required_fields=self.required)
        out2 = self.head.process(di2).to_dict()

        # score unchanged
        self.assertEqual(score, out2['validation_score'])
        # classification should have flipped to 'rejected' if threshold > score
        if self.head.config.validation_threshold > score:
            self.assertEqual(out2['status'], 'rejected')
        else:
            self.assertEqual(out2['status'], 'accepted')

if __name__ == '__main__':
    unittest.main()
