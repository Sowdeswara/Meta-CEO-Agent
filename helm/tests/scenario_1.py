"""
Test Scenario 1 - Complete System Integration Test
Verifies all HELM v2.0 components work together
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helm import HELM
from helm.logger import get_logger

logger = get_logger(__name__)


def test_scenario_1_system_integration():
    """Test: Complete HELM system integration"""
    
    try:
        logger.info("\n" + "="*70)
        logger.info("SCENARIO 1: COMPLETE SYSTEM INTEGRATION TEST")
        logger.info("="*70)
        
        # Test 1: Initialize HELM
        logger.info("\n[TEST 1] Initializing HELM v2.0...")
        from helm.config import Config
        config = Config()
        config.DEVELOPMENT_MODE = True

        helm = HELM(enable_local_model=True, enable_dashboard=False, skip_system_check=True, config=config)
        logger.info("[OK] HELM initialized successfully")
        
        # Test 2: Process a strategic decision
        logger.info("\n[TEST 2] Processing strategic decision...")
        strategic_prompt = "Should we expand into the Southeast market?"
        strategic_context = {
            'user_id': 'user_001',
            'session_id': 'session_001',
            'objectives': ['Expand market share', 'Increase revenue by 20%'],
            'constraints': ['Budget limit: $500K', 'Timeline: 12 months'],
            'resources': ['Marketing team', 'Sales force', 'Technology platform'],
            'timeline': 'Q2-Q3 2024',
            'risk_tolerance': 'medium'
        }
        required_fields_strategy = ['objectives', 'constraints', 'resources']
        
        decision1 = helm.process_decision(
            strategic_prompt,
            strategic_context,
            required_fields_strategy
        )
        
        logger.info(f"[OK] Strategic decision processed")
        logger.info(f"  Decision ID: {decision1['decision_id']}")
        logger.info(f"  Agent: {decision1['agent_used']}")
        logger.info(f"  Status: {decision1['status']}")
        logger.info(f"  Confidence: {decision1['confidence']:.2%}")
        
        # Test 3: Process a financial decision
        logger.info("\n[TEST 3] Processing financial decision...")
        financial_prompt = "What is the ROI on this $100K investment?"
        financial_context = {
            'user_id': 'user_002',
            'session_id': 'session_002',
            'revenue': 500000,
            'costs': 300000,
            'investment': 100000,
            'expected_returns': 180000,
            'timeframe_years': 3
        }
        required_fields_finance = ['revenue', 'costs', 'investment', 'expected_returns']
        
        decision2 = helm.process_decision(
            financial_prompt,
            financial_context,
            required_fields_finance
        )
        
        logger.info(f"[OK] Financial decision processed")
        logger.info(f"  Decision ID: {decision2['decision_id']}")
        logger.info(f"  Agent: {decision2['agent_used']}")
        logger.info(f"  ROI Estimate: {decision2['roi_estimate']:.2%}")
        logger.info(f"  Risk Level: {decision2['risk_level']}")
        
        # Test 4: Retrieve decision history
        logger.info("\n[TEST 4] Retrieving decision history...")
        history = helm.get_decision_history(limit=5)
        logger.info(f"[OK] Retrieved {len(history)} decisions from database")
        
        # Test 5: Get system statistics
        logger.info("\n[TEST 5] Getting system statistics...")
        stats = helm.get_statistics()
        logger.info(f"[OK] Statistics retrieved:")
        logger.info(f"  Total decisions: {stats.get('total_decisions', 0)}")
        logger.info(f"  Accepted: {stats.get('accepted_decisions', 0)}")
        logger.info(f"  Rejected: {stats.get('rejected_decisions', 0)}")
        logger.info(f"  Avg confidence: {stats.get('average_confidence', 0):.2%}")
        logger.info(f"  Avg ROI: {stats.get('average_roi', 0):.2%}")
        
        # Test 6: Shutdown
        logger.info("\n[TEST 6] Shutting down HELM...")
        helm.shutdown()
        logger.info("[OK] HELM shutdown complete")
        
        logger.info("\n" + "="*70)
        logger.info("SCENARIO 1: ALL TESTS PASSED [OK]")
        logger.info("="*70 + "\n")
        
        return True
    
    except Exception as e:
        logger.error(f"SCENARIO 1 FAILED: {e}", exc_info=True)
        logger.info("="*70 + "\n")
        return False


if __name__ == "__main__":
    success = test_scenario_1_system_integration()
    sys.exit(0 if success else 1)
