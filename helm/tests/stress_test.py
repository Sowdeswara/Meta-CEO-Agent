"""
Stress Test - deterministic randomized decision inputs
Runs 50 inputs plus deliberate failure scenarios
"""

import logging
import sys
from pathlib import Path
from random import Random

# Add package root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helm import HELM
from helm.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_stress_test(seed: int = 12345, runs: int = 50):
    config = Config()
    config.DEVELOPMENT_MODE = True

    helm = HELM(enable_local_model=False, enable_dashboard=False, skip_system_check=True, config=config)

    rng = Random(seed)

    accepted = 0
    rejected = 0
    escalated = 0
    scores = []

    required_fields = ['revenue', 'costs', 'investment', 'expected_returns']

    for i in range(runs):
        # Deterministic randomized inputs
        revenue = round(rng.uniform(0, 1_000_000), 2)
        costs = round(rng.uniform(0, revenue + 100_000), 2)
        investment = round(rng.uniform(0, 500_000), 2)
        expected_returns = round(rng.uniform(0, 2_000_000), 2)
        timeframe_years = rng.randint(1, 10)

        context = {
            'user_id': f'user_{i:03d}',
            'session_id': f'sess_{i:03d}',
            'revenue': revenue,
            'costs': costs,
            'investment': investment,
            'expected_returns': expected_returns,
            'timeframe_years': timeframe_years,
            'confidence': round(rng.uniform(0.0, 1.0), 2),
            'roi': round((expected_returns - investment) / (investment if investment else 1), 2)
        }

        try:
            decision = helm.process_decision(f"Stress test {i}", context, required_fields)
            status = decision.get('status', 'rejected')
            score = decision.get('validation_score', 0)
            scores.append(score)
            # Debug instrumentation for first 10 cases
            if i < 10:
                th = config.validation_threshold
                print(f"Case {i+1}:\nscore={score:.2f} threshold={th:.2f} status={status.upper()}\n")

            if status == 'accepted':
                accepted += 1
            elif status == 'rejected':
                rejected += 1
            elif status == 'escalated':
                escalated += 1
        except Exception as e:
            logger.exception(f"Unhandled exception during stress iteration {i}: {e}")

    # PHASE 3 - deliberate failure scenarios
    failure_cases = [
        ({'revenue': None}, 'missing_fields'),
        ({'revenue': 'not_a_number', 'costs': 'x'}, 'non_numeric'),
        ({'revenue': -10000, 'costs': 20000}, 'negative_revenue'),
        ({'investment': 10**12, 'expected_returns': 1}, 'extremely_large_investment'),
        ({'revenue': 1000, 'costs': 1000, 'investment': 0, 'expected_returns': 0}, 'zero_division_risk'),
        ({'revenue': 100, 'costs': 50, 'investment': 1000, 'expected_returns': 0, 'confidence': 0.1}, 'low_confidence'),
    ]

    for i, (ctx_partial, label) in enumerate(failure_cases):
        ctx = {
            'user_id': f'fail_{i}',
            'session_id': f'fail_sess_{i}',
            'revenue': ctx_partial.get('revenue', 0),
            'costs': ctx_partial.get('costs', 0),
            'investment': ctx_partial.get('investment', 0),
            'expected_returns': ctx_partial.get('expected_returns', 0),
            'timeframe_years': ctx_partial.get('timeframe_years', 1),
            'confidence': ctx_partial.get('confidence', 0.5),
            'roi': ctx_partial.get('roi', 0)
        }

        try:
            decision = helm.process_decision(f"Failure case {label}", ctx, required_fields)
            status = decision.get('status', 'rejected')
            logger.info(f"Failure case {label} -> status: {status}, score: {decision.get('validation_score')}")
        except Exception as e:
            logger.exception(f"Failure case {label} caused exception: {e}")

    avg_score = sum(scores) / len(scores) if scores else 0.0

    summary = {
        'accepted': accepted,
        'rejected': rejected,
        'escalated': escalated,
        'average_validation_score': round(avg_score, 4)
    }

    logger.info(f"Stress test summary: {summary}")
    print(summary)
    return summary


if __name__ == '__main__':
    run_stress_test()
