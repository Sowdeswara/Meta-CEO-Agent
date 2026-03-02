import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.arbitration.arbitrator import ArbitrationEngine
from helm.config import Config
from helm.schemas import StructuredDecision, DecisionStatus, AgentType


def make_fin(roi, score):
    return StructuredDecision(
        decision_id='f',
        agent_used=AgentType.FINANCE,
        decision_text='',
        confidence=0.5,
        risk_level='medium',
        roi_estimate=roi,
        reasoning={},
        validation_score=score,
        status=DecisionStatus.PENDING
    )

def make_strat(score):
    return StructuredDecision(
        decision_id='s',
        agent_used=AgentType.STRATEGY,
        decision_text='',
        confidence=0.5,
        risk_level='low',
        roi_estimate=0.0,
        reasoning={},
        validation_score=score,
        status=DecisionStatus.PENDING
    )

class RiskAdjustmentTests(unittest.TestCase):
    def setUp(self):
        cfg = Config()
        cfg.ARBITRATION_WEIGHTS = {'strategy': 0.5, 'finance': 0.5}
        cfg.RISK_PENALTY_FACTOR = 0.5
        self.eng = ArbitrationEngine(cfg)

    def test_zero_risk(self):
        # risk_score = 1 - validation_score; use val_score=1 -> risk=0
        fin = make_fin(roi=2.0, score=1.0)
        strat = make_strat(score=0.0)
        out = self.eng.compute(strat, fin)
        # adjusted_roi should equal roi
        self.assertAlmostEqual(out['finance_component'], 0.5 * 2.0)

    def test_high_risk(self):
        # validation_score=0 -> risk_score=1 -> penalty=0.5
        fin = make_fin(roi=2.0, score=0.0)
        strat = make_strat(score=0.0)
        out = self.eng.compute(strat, fin)
        # adjusted_roi = 2*(1-0.5)=1
        self.assertAlmostEqual(out['finance_component'], 0.5 * 1.0)

if __name__ == '__main__':
    unittest.main()
