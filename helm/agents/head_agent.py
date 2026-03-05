"""
Head Agent - Orchestrates and supervises other agents
Deterministic task classification and routing
"""

import logging
import uuid
from typing import Dict, Any

from ..schemas import (
    AgentType, DecisionStatus, StructuredDecision, DecisionInput
)
from ..validation.validator import Validator
from ..arbitration.arbitrator import ArbitrationEngine


logger = logging.getLogger(__name__)


class HeadAgent:
    """Orchestration agent that supervises and routes to specialized agents"""
    
    def __init__(self, config=None, validator: Validator = None):
        """Initialize HeadAgent
        
        Args:
            config: Configuration object
            validator: Validator instance
        """
        self.config = config
        self.validator = validator or Validator(config)
        # initialize arbitration engine for v3 deterministic arbitration
        from ..arbitration.arbitrator import ArbitrationEngine
        self.arbitrator = ArbitrationEngine(config)
        self.agents = {}  # Will be populated with strategy and finance agents
        self.max_retries = config.max_retries if config else 2
        self.decision_history = []
    
    def register_agent(self, agent_type: AgentType, agent):
        """Register a specialized agent
        
        Args:
            agent_type: Type of agent (STRATEGY, FINANCE, etc.)
            agent: Agent instance
        """
        self.agents[agent_type] = agent
        logger.info(f"Registered agent: {agent_type.value}")
    
    def classify_task(self, prompt: str) -> AgentType:
        """Classify task to appropriate agent using deterministic rules
        
        Args:
            prompt: Input prompt from user
            
        Returns:
            AgentType: Classified agent type
        """
        prompt_lower = prompt.lower()
        
        # Deterministic keyword-based classification
        finance_keywords = ['profit', 'revenue', 'cost', 'margin', 'financial', 'roi', 'cashflow', 'debt', 'equity']
        product_keywords = ['product', 'development', 'innovation', 'features', 'supply', 'chain', 'efficiency']
        competitive_keywords = ['competition', 'competitor', 'market', 'share', 'positioning', 'advantage']
        market_keywords = ['market', 'growth', 'demand', 'intelligence', 'forecast', 'trends']
        
        finance_score = sum(1 for kw in finance_keywords if kw in prompt_lower)
        product_score = sum(1 for kw in product_keywords if kw in prompt_lower)
        competitive_score = sum(1 for kw in competitive_keywords if kw in prompt_lower)
        market_score = sum(1 for kw in market_keywords if kw in prompt_lower)
        
        # Find the highest scoring category
        scores = {
            'finance': finance_score,
            'product': product_score, 
            'competitive': competitive_score,
            'market': market_score
        }
        max_category = max(scores, key=scores.get)
        
        if max_category == 'finance':
            agent_type = AgentType.FINANCE_OPTIMIZATION
        elif max_category == 'product':
            agent_type = AgentType.PRODUCT_STRATEGY
        elif max_category == 'competitive':
            agent_type = AgentType.COMPETITIVE_STRATEGY
        elif max_category == 'market':
            agent_type = AgentType.MARKET_INTELLIGENCE
        else:
            agent_type = AgentType.PRODUCT_STRATEGY  # Default
        
        logger.info(f"Task classified as: {agent_type.value} (scores: finance={finance_score}, product={product_score}, competitive={competitive_score}, market={market_score})")
        return agent_type
    
    def process(self, decision_input: DecisionInput) -> StructuredDecision:
        """Process input and orchestrate agent responses
        
        Args:
            decision_input: Input decision request
            
        Returns:
            StructuredDecision: Final structured decision
        """
        decision_id = str(uuid.uuid4())[:8]
        logger.info(f"Processing decision {decision_id}: {decision_input.prompt[:50]}...")
        
        # Step 1: Validate input (pre-arbitration)
        input_validation = self.validator.validate_decision(
            decision_input.context,
            decision_input.required_fields,
            self.max_retries
        )
        logger.info(f"Input validation result: {input_validation.status.value} (score: {input_validation.score.weighted_score:.2f})")
        if not input_validation.passed(self.config.validation_threshold if self.config else 0.70):
            logger.warning(f"Validation failed for decision {decision_id}")
            return StructuredDecision(
                decision_id=decision_id,
                agent_used=AgentType.HEAD,
                decision_text="Validation failed. Input does not meet requirements.",
                confidence=0.0,
                risk_level="high",
                roi_estimate=0.0,
                reasoning={'validation': input_validation.to_dict()},
                validation_score=input_validation.score.weighted_score,
                status=DecisionStatus.REJECTED
            )
        
        # Step 1.5: Derive market signals from business inputs
        derived_signals = self._derive_market_signals(decision_input.context)
        decision_input.context.update(derived_signals)
        logger.info(f"Derived market signals: {derived_signals}")
        
        # Step 2: Run all specialized agents (if available)
        product_dec = None
        competitive_dec = None
        market_dec = None
        finance_dec = None
        if AgentType.PRODUCT_STRATEGY in self.agents:
            product_dec = self.agents[AgentType.PRODUCT_STRATEGY].process(decision_input)
        if AgentType.COMPETITIVE_STRATEGY in self.agents:
            competitive_dec = self.agents[AgentType.COMPETITIVE_STRATEGY].process(decision_input)
        if AgentType.MARKET_INTELLIGENCE in self.agents:
            market_dec = self.agents[AgentType.MARKET_INTELLIGENCE].process(decision_input)
        if AgentType.FINANCE_OPTIMIZATION in self.agents:
            finance_dec = self.agents[AgentType.FINANCE_OPTIMIZATION].process(decision_input)

        # Step 3: Arbitration
        arb_output = self.arbitrator.compute_multi(
            product_dec or self._default_decision(decision_id, AgentType.PRODUCT_STRATEGY, decision_input),
            competitive_dec or self._default_decision(decision_id, AgentType.COMPETITIVE_STRATEGY, decision_input),
            market_dec or self._default_decision(decision_id, AgentType.MARKET_INTELLIGENCE, decision_input),
            finance_dec or self._default_decision(decision_id, AgentType.FINANCE_OPTIMIZATION, decision_input)
        )
        # add arbitration score to context for validation
        decision_input.context['arbitration_score'] = arb_output['composite_score']

        # re-run validation with arbitration score included
        validation_result = self.validator.validate_decision(
            decision_input.context,
            decision_input.required_fields,
            self.max_retries
        )
        logger.info(f"Post-arbitration validation result: {validation_result.status.value} (score: {validation_result.score.weighted_score:.2f})")

        # pick dominant decision for output
        dominant_factor = arb_output['dominant_factor']
        if dominant_factor == 'finance_optimization':
            decision = finance_dec
        elif dominant_factor == 'product_strategy':
            decision = product_dec
        elif dominant_factor == 'competitive_strategy':
            decision = competitive_dec
        elif dominant_factor == 'market_intelligence':
            decision = market_dec
        else:
            decision = finance_dec  # fallback to finance
        
        if decision is None:
            decision = self._default_decision(decision_id, AgentType.HEAD, decision_input)

        # attach arbitration results
        if isinstance(decision.reasoning, dict):
            decision.reasoning['arbitration'] = arb_output

        # Ensure the decision carries the validator's authoritative score
        try:
            decision.validation_score = validation_result.score.weighted_score
            if isinstance(decision.reasoning, dict):
                decision.reasoning['validation'] = validation_result.to_dict()
        except Exception:
            # best-effort assignment; do not fail processing for instrumentation
            logger.debug("Failed to attach validator score to decision object")

        # Step 4: Validate decision output
        output_valid, output_msg = self.validator.validate_output(decision.to_dict())
        
        if not output_valid:
            logger.error(f"Output validation failed: {output_msg}")
            decision.status = DecisionStatus.REJECTED
        else:
            decision.status = DecisionStatus.ACCEPTED
        
        # Step 5: Store in history
        self.decision_history.append(decision)
        logger.info(f"Decision {decision_id} processed with status: {decision.status.value}")
        
        return decision
    
    def _route_to_agent(
        self,
        decision_id: str,
        agent_type: AgentType,
        decision_input: DecisionInput,
        validation_result: Any
    ) -> StructuredDecision:
        """Route decision to appropriate specialized agent
        
        Args:
            decision_id: Decision ID
            agent_type: Target agent type
            decision_input: Decision input
            validation_result: Validation result
            
        Returns:
            StructuredDecision: Agent's decision
        """
        try:
            # Get the agent
            agent = self.agents.get(agent_type)
            
            if not agent:
                logger.warning(f"Agent {agent_type.value} not registered, using HEAD logic")
                return self._default_decision(decision_id, agent_type, decision_input)
            
            # Let agent process the decision
            decision = agent.process(decision_input)
            
            logger.info(f"Agent {agent_type.value} processed decision {decision_id}")
            return decision
        
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return self._escalate_decision(decision_id, agent_type, str(e))
    
    def _default_decision(
        self,
        decision_id: str,
        agent_type: AgentType,
        decision_input: DecisionInput
    ) -> StructuredDecision:
        """Generate default decision when agent is unavailable
        
        Args:
            decision_id: Decision ID
            agent_type: Agent type
            decision_input: Decision input
            
        Returns:
            StructuredDecision: Default decision
        """
        return StructuredDecision(
            decision_id=decision_id,
            agent_used=agent_type,
            decision_text="Default decision: Further analysis required.",
            confidence=0.5,
            risk_level="medium",
            roi_estimate=0.0,
            reasoning={'note': 'Default decision due to unavailable agent'},
            validation_score=0.5,
            status=DecisionStatus.PENDING
        )
    
    def _escalate_decision(
        self,
        decision_id: str,
        agent_type: AgentType,
        error: str
    ) -> StructuredDecision:
        """Escalate decision on error
        
        Args:
            decision_id: Decision ID
            agent_type: Agent type
            error: Error message
            
        Returns:
            StructuredDecision: Escalated decision
        """
        logger.error(f"Escalating decision {decision_id}: {error}")
        return StructuredDecision(
            decision_id=decision_id,
            agent_used=AgentType.ESCALATION,
            decision_text=f"Decision escalated due to error: {error[:100]}",
            confidence=0.0,
            risk_level="high",
            roi_estimate=0.0,
            reasoning={'error': error, 'escalated_from': agent_type.value},
            validation_score=0.0,
            status=DecisionStatus.ESCALATED
        )
    
    def _derive_market_signals(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Derive market signals from business inputs
        
        Args:
            context: Business context with revenue, costs, investment, etc.
            
        Returns:
            Dict with derived market signals
        """
        revenue = context.get('revenue', 0)
        costs = context.get('costs', 0)
        investment = context.get('investment', 0)
        expected_returns = context.get('expected_returns', 0)
        
        # Derive signals using business logic
        demand_index = min(expected_returns / max(investment, 1), 1.0)
        competitor_strength = min(costs / max(revenue, 1), 1.0)
        market_growth = min((expected_returns - investment) / max(investment, 1), 1.0)
        product_innovation = 0.5 + (expected_returns / max(investment, 1)) * 0.3
        product_innovation = min(product_innovation, 1.0)
        supply_chain_efficiency = max(0.3, revenue / max(costs, 1))
        supply_chain_efficiency = min(supply_chain_efficiency, 1.0)
        
        return {
            'market_growth': market_growth,
            'demand_index': demand_index,
            'competitor_strength': competitor_strength,
            'product_innovation': product_innovation,
            'supply_chain_efficiency': supply_chain_efficiency
        }
    
    def validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate agent outputs
        
        Args:
            result: Agent result to validate
            
        Returns:
            bool: True if valid
        """
        required_fields = ['decision_text', 'confidence', 'reasoning']
        
        for field in required_fields:
            if field not in result:
                logger.error(f"Missing required field in result: {field}")
                return False
        
        try:
            confidence = float(result.get('confidence', 0))
            if not (0 <= confidence <= 1):
                logger.error(f"Invalid confidence: {confidence}")
                return False
        except (ValueError, TypeError):
            logger.error("Confidence not numeric")
            return False
        
        logger.debug("Result validation passed")
        return True
