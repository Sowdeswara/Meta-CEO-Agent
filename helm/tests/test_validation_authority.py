import unittest
import sys, os
# ensure package root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.agents.head_agent import HeadAgent
from helm.validation.validator import Validator
from helm.schemas import AgentType, DecisionInput
from helm.config import Config


class FakeAgent:
    def __init__(self, fake_score):
        self.fake_score = fake_score

    def process(self, decision_input: DecisionInput):
        # return a StructuredDecision-like object
        from helm.schemas import StructuredDecision, DecisionStatus

        return StructuredDecision(
            decision_id="fake",
            agent_used=AgentType.STRATEGY,
            decision_text="fake",
            confidence=1.0,
            risk_level="low",
            roi_estimate=0.0,
            reasoning={},
            validation_score=self.fake_score,
            status=DecisionStatus.PENDING,
        )


class ValidationAuthorityTests(unittest.TestCase):
    def setUp(self):
        config = Config()
        config.DEVELOPMENT_MODE = True
        self.head = HeadAgent(config=config, validator=Validator(config))
        # register a dummy agent with deterministic output
        self.head.register_agent(AgentType.STRATEGY, FakeAgent(fake_score=0.01))

    def test_validator_score_overrides_agent(self):
        # create decision input with values guaranteeing high validator score
        context = {
            'user_id': 'u',
            'session_id': 's',
            'revenue': 1000,
            'costs': 500,
            'investment': 100,
            'expected_returns': 2000,
            'timeframe_years': 1,
            'confidence': 0.9,
            'roi': 10.0,
        }
        required = ['revenue', 'costs', 'investment', 'expected_returns']

        from helm.schemas import DecisionInput
        di = DecisionInput(prompt='test', context=context, user_id='u', session_id='s', required_fields=required)
        result = self.head.process(di).to_dict()

        # validator should compute score >> threshold (~0.9) even though agent fake_score=0.01
        self.assertGreater(result['validation_score'], self.head.config.validation_threshold)
        self.assertEqual(result['status'], 'accepted')
        self.assertNotEqual(result['validation_score'], 0.01)


if __name__ == '__main__':
    unittest.main()
