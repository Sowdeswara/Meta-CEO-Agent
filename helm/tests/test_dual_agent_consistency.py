import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.arbitration.arbitrator import ArbitrationEngine
from helm.config import Config
from helm.schemas import StructuredDecision, DecisionStatus, AgentType


def make_dec(score, roi=0.0, confidence=0.5):
    return StructuredDecision(
        decision_id='x',
        agent_used=AgentType.STRATEGY,
        decision_text='',
        confidence=confidence,
        risk_level='low',
        roi_estimate=roi,
        reasoning={},
        validation_score=score,
        status=DecisionStatus.PENDING
    )

class DualAgentConsistencyTests(unittest.TestCase):
    def setUp(self):
        cfg = Config()
        cfg.ARBITRATION_WEIGHTS = {'strategy': 0.5, 'finance': 0.5}
        cfg.RISK_PENALTY_FACTOR = 0.5
        self.eng = ArbitrationEngine(cfg)
        # sample outputs
        self.strat = make_dec(score=0.7, roi=0.0, confidence=0.6)
        self.fin = make_dec(score=0.0, roi=1.5, confidence=0.4)

    def test_deterministic_same_input(self):
        scores = [self.eng.compute(self.strat, self.fin)['composite_score'] for _ in range(5)]
        self.assertTrue(all(s == scores[0] for s in scores))

    def test_order_independence(self):
        s1 = self.eng.compute(self.strat, self.fin)['composite_score']
        s2 = self.eng.compute(self.fin, self.strat)['composite_score']
        self.assertEqual(s1, s2)

if __name__ == '__main__':
    unittest.main()
