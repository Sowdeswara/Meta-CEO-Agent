"""Simple local demo script for HELM agents and arbitration

Run this file to exercise the system entirely on a local machine
(no GPU, no network calls required).

Usage:
    python local_demo.py
"""

from helm.config import Config
from helm.agents.head_agent import HeadAgent
from helm.agents.strategy_agent import StrategyAgent
from helm.agents.finance_agent import FinanceAgent
from helm.schemas import DecisionInput, AgentType


def main():
    cfg = Config()
    cfg.DEVELOPMENT_MODE = True
    cfg.DEMO_MODE = True
    cfg.USE_GPU = False
    cfg.USE_LOCAL_MODEL = True

    head = HeadAgent(cfg)
    head.register_agent(AgentType.STRATEGY, StrategyAgent(cfg))
    head.register_agent(AgentType.FINANCE, FinanceAgent(cfg))

    # craft a sample decision input
    context = {
        'objectives': ['increase market share', 'reduce costs'],
        'constraints': ['limited budget'],
        'resources': ['team', 'capital'],
        'timeline': 'within quarter',
        'revenue': 100000,
        'costs': 60000,
        'investment': 50000,
        'expected_returns': 120000,
        'timeframe_years': 1
    }
    di = DecisionInput(
        prompt="Should we pursue the new expansion strategy",
        context=context,
        user_id="user123",
        session_id="sess456",
        required_fields=['objectives', 'revenue', 'costs']
    )

    result = head.process(di)

    print("\n=== Decision Output ===")
    print(result.to_dict())
    print("Arbitration reasoning:", result.reasoning.get('arbitration'))
    print("Validator info:", result.reasoning.get('validation'))


if __name__ == '__main__':
    main()
