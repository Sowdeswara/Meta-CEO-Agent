import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.arbitration.arbitrator import ArbitrationEngine
from helm.config import Config
from helm.schemas import StructuredDecision, DecisionStatus, AgentType


def make_dec(score, confidence=0.5, roi=0.0):
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


class ArbitrationWeightsTests(unittest.TestCase):
    def test_weights_sum(self):
        cfg = Config()
        cfg.ARBITRATION_WEIGHTS = {'strategy': 0.6, 'finance': 0.4}
        eng = ArbitrationEngine(cfg)
        self.assertAlmostEqual(eng.weights['strategy'] + eng.weights['finance'], 1.0)
        # invalid should raise
        cfg.ARBITRATION_WEIGHTS = {'strategy': 0.6, 'finance': 0.5}
        with self.assertRaises(ValueError):
            ArbitrationEngine(cfg)

    def test_composite_score(self):
        cfg = Config()
        cfg.ARBITRATION_WEIGHTS = {'strategy': 0.5, 'finance': 0.5}
        cfg.RISK_PENALTY_FACTOR = 0.5
        eng = ArbitrationEngine(cfg)
        strat = make_dec(score=0.8, confidence=0.7)
        fin = make_dec(score=0.0, confidence=0.3, roi=2.0)
        # risk_score = 1 - 0.0 = 1.0, normalized_risk=1
        # risk_penalty=0.5, adjusted_roi=2.0*(1-0.5)=1.0
        # composite=0.5*0.8 + 0.5*1.0 = 0.9
        out = eng.compute(strat, fin)
        self.assertAlmostEqual(out['composite_score'], 0.9)
        self.assertEqual(out['dominant_factor'], 'finance')
        self.assertAlmostEqual(out['confidence'], 0.5)


if __name__ == '__main__':
    unittest.main()
