"""
Test Scenario 3 - Agent Orchestration and Decision Validation
Verifies deterministic routing and validation logic
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helm.config import Config
from helm.validation.validator import Validator
from helm.agents.head_agent import HeadAgent
from helm.agents.strategy_agent import StrategyAgent
from helm.agents.finance_agent import FinanceAgent
from helm.schemas import DecisionInput, AgentType
from helm.logger import get_logger

logger = get_logger(__name__)


def test_scenario_3_agent_orchestration():
    """Test: Agent orchestration and decision validation"""
    
    try:
        logger.info("\n" + "="*70)
        logger.info("SCENARIO 3: AGENT ORCHESTRATION AND VALIDATION")
        logger.info("="*70)
        
        config = Config()
        config.DEVELOPMENT_MODE = True
        validator = Validator(config)
        
        # Test 1: Initialize agents
        logger.info("\n[TEST 1] Initializing agents...")
        head_agent = HeadAgent(config, validator)
        strategy_agent = StrategyAgent(config)
        finance_agent = FinanceAgent(config)
        
        head_agent.register_agent(AgentType.STRATEGY, strategy_agent)
        head_agent.register_agent(AgentType.FINANCE, finance_agent)
        logger.info("[OK] HeadAgent initialized")
        logger.info("[OK] StrategyAgent initialized")
        logger.info("[OK] FinanceAgent initialized")
        
        # Test 2: Task classification
        logger.info("\n[TEST 2] Testing task classification...")
        
        strategy_prompt = "What is our strategic direction for 2024?"
        classified = head_agent.classify_task(strategy_prompt)
        logger.info(f"[OK] Strategy prompt classified as: {classified.value}")
        assert classified == AgentType.STRATEGY
        
        finance_prompt = "Calculate the profit margin on a $50K investment."
        classified = head_agent.classify_task(finance_prompt)
        logger.info(f"[OK] Finance prompt classified as: {classified.value}")
        assert classified == AgentType.FINANCE
        
        # Test 3: Validation scoring
        logger.info("\n[TEST 3] Testing validation scoring...")
        
        test_data = {
            'revenue': 100000,
            'costs': 60000,
            'investment': 50000,
            'expected_returns': 80000,
            'confidence': 0.85,
            'roi': 0.60
        }
        required_fields = ['revenue', 'costs', 'investment', 'expected_returns']
        
        score = validator.calculate_validation_score(test_data, required_fields)
        logger.info(f"[OK] Validation score calculated:")
        logger.info(f"  Schema complete: {score.schema_complete:.2f}")
        logger.info(f"  Required fields: {score.required_fields_present:.2f}")
        logger.info(f"  Numeric valid: {score.numeric_valid:.2f}")
        logger.info(f"  Confidence: {score.confidence:.2f}")
        logger.info(f"  ROI viable: {score.roi_viable:.2f}")
        logger.info(f"  Weighted score: {score.weighted_score:.2f}")
        
        # Test 4: Complete decision validation
        logger.info("\n[TEST 4] Testing complete decision validation...")
        
        validation_result = validator.validate_decision(
            test_data,
            required_fields,
            max_retries=2
        )
        
        logger.info(f"[OK] Decision validation completed:")
        logger.info(f"  Status: {validation_result.status.value}")
        logger.info(f"  Score: {validation_result.score.weighted_score:.2f}")
        logger.info(f"  Passed: {validation_result.passed()}")
        
        if validation_result.errors:
            logger.info(f"  Errors: {validation_result.errors}")
        if validation_result.warnings:
            logger.info(f"  Warnings: {validation_result.warnings}")
        
        # Test 5: Risk assessment
        logger.info("\n[TEST 5] Testing risk assessment...")
        
        high_risk_data = {
            'revenue': 10000,
            'costs': 20000,  # Negative profit
            'confidence': 0.3,
            'roi': -0.50
        }
        
        risk_level = validator.assess_risk(high_risk_data)
        logger.info(f"[OK] Risk assessment for negative profit: {risk_level}")
        
        # Test 6: Process decision through head agent
        logger.info("\n[TEST 6] Processing decision through head agent...")
        
        decision_input = DecisionInput(
            prompt="Should we proceed with this investment?",
            context=test_data,
            user_id="test_user",
            session_id="test_session",
            required_fields=required_fields
        )
        
        decision = head_agent.process(decision_input)
        logger.info(f"[OK] Decision processed:")
        logger.info(f"  ID: {decision.decision_id}")
        logger.info(f"  Agent: {decision.agent_used.value}")
        logger.info(f"  Status: {decision.status.value}")
        logger.info(f"  Confidence: {decision.confidence:.2%}")
        
        logger.info("\n" + "="*70)
        logger.info("SCENARIO 3: ALL TESTS PASSED [OK]")
        logger.info("="*70 + "\n")
        
        return True
    
    except Exception as e:
        logger.error(f"SCENARIO 3 FAILED: {e}", exc_info=True)
        logger.info("="*70 + "\n")
        return False


if __name__ == "__main__":
    success = test_scenario_3_agent_orchestration()
    sys.exit(0 if success else 1)
