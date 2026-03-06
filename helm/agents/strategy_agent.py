"""
Product Strategy Agent - Handles product-focused strategic analysis and planning
Deterministic strategic reasoning for product development and positioning
"""

import logging
import uuid
from typing import Dict, Any

from ..schemas import (
    AgentType, DecisionStatus, StructuredDecision, DecisionInput
)


logger = logging.getLogger(__name__)


class ProductStrategyAgent:
    """Agent responsible for product-focused strategic analysis and planning"""

    def __init__(self, config=None, llm=None):
        """Initialize ProductStrategyAgent

        Args:
            config: Configuration object
            llm: Optional LLM for explanation generation
        """
        self.config = config
        self.llm = llm
        self.agent_type = AgentType.PRODUCT_STRATEGY

    def process(self, decision_input: DecisionInput) -> StructuredDecision:
        """Process product strategy decision request

        Args:
            decision_input: Input decision request

        Returns:
            StructuredDecision: Product strategy decision
        """
        decision_id = str(uuid.uuid4())[:8]

        try:
            # Step 1: Extract product strategic factors
            product_factors = self._extract_factors(decision_input.context)

            # Step 2: Perform product strategy analysis
            analysis = self._analyze_product_strategy(product_factors)

            # Step 3: Generate recommendation
            recommendation = self._generate_recommendation(analysis)

            # Step 4: Generate explanation (if LLM available)
            explanation = ""
            if self.llm:
                explanation = self._generate_explanation(recommendation, analysis)

            # Step 5: Create decision
            decision = StructuredDecision(
                decision_id=decision_id,
                agent_used=self.agent_type,
                decision_text=recommendation.get('text', 'No recommendation'),
                confidence=recommendation.get('confidence', 0.5),
                risk_level=recommendation.get('risk_level', 'medium'),
                roi_estimate=recommendation.get('roi_estimate', 0.0),
                reasoning={
                    'factors': product_factors,
                    'analysis': analysis,
                    'explanation': explanation
                },
                validation_score=analysis.get('product_strategy_score', 0.5),
                status=DecisionStatus.PENDING
            )

            logger.info(f"Product strategy decision {decision_id} generated (confidence: {decision.confidence:.2f})")
            return decision

        except Exception as e:
            logger.error(f"Product strategy processing failed: {e}")
            raise

    def _extract_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product strategic factors from context

        Args:
            context: Decision context

        Returns:
            Dict with extracted product strategic factors
        """
        market_signals = context.get('market_signals', {})
        factors = {
            'objectives': context.get('objectives', []),
            'constraints': context.get('constraints', []),
            'resources': context.get('resources', []),
            'timeline': context.get('timeline', ''),
            'stakeholders': context.get('stakeholders', []),
            'risk_tolerance': context.get('risk_tolerance', 'medium'),
            'product_innovation': market_signals.get('product_innovation', 0.5),
            'supply_chain_efficiency': market_signals.get('supply_chain_efficiency', 0.5)
        }

        logger.debug(f"Extracted product factors: {len(factors)} categories")
        return factors

    def _analyze_product_strategy(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Perform product strategy analysis using deterministic rules

        Args:
            factors: Product strategic factors

        Returns:
            Dict with analysis results
        """
        analysis = {
            'feasibility_score': 0.0,
            'alignment_score': 0.0,
            'resource_score': 0.0,
            'timeline_score': 0.0,
            'innovation_score': 0.0,
            'supply_chain_score': 0.0,
            'product_strategy_score': 0.0
        }

        # Feasibility assessment (0-1)
        num_objectives = len(factors.get('objectives', []))
        num_constraints = len(factors.get('constraints', []))
        analysis['feasibility_score'] = max(1.0 - (num_constraints / max(num_objectives, 1)) * 0.5, 0.0)

        # Resource alignment (0-1)
        num_resources = len(factors.get('resources', []))
        analysis['resource_score'] = min(num_resources / 3, 1.0)  # Assume 3 resources is optimal

        # Timeline assessment (0-1)
        timeline = factors.get('timeline', '')
        if timeline:
            # Simple heuristic: shorter timelines get lower scores
            timeline_lower = timeline.lower()
            if 'immediately' in timeline_lower or 'urgent' in timeline_lower:
                analysis['timeline_score'] = 0.6
            elif 'week' in timeline_lower:
                analysis['timeline_score'] = 0.8
            elif 'month' in timeline_lower or 'quarter' in timeline_lower:
                analysis['timeline_score'] = 0.9
            else:
                analysis['timeline_score'] = 0.7
        else:
            analysis['timeline_score'] = 0.5

        # Innovation score (0-1)
        innovation = factors.get('product_innovation', 0.5)
        analysis['innovation_score'] = min(max(innovation, 0.0), 1.0)

        # Supply chain efficiency (0-1)
        supply_chain = factors.get('supply_chain_efficiency', 0.5)
        analysis['supply_chain_score'] = min(max(supply_chain, 0.0), 1.0)

        # Overall product strategy score (weighted average)
        analysis['product_strategy_score'] = (
            analysis['feasibility_score'] * 0.25 +
            analysis['resource_score'] * 0.20 +
            analysis['timeline_score'] * 0.15 +
            analysis['innovation_score'] * 0.20 +
            analysis['supply_chain_score'] * 0.20
        )

        logger.debug(f"Product strategy analysis: feasibility={analysis['feasibility_score']:.2f}, innovation={analysis['innovation_score']:.2f}, product_strategy={analysis['product_strategy_score']:.2f}")

        return analysis

    def _generate_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product strategy recommendation

        Args:
            analysis: Analysis results

        Returns:
            Dict with recommendation
        """
        product_strategy_score = analysis.get('product_strategy_score', 0.5)

        # Deterministic recommendation rules
        if product_strategy_score >= 0.8:
            recommendation = {
                'text': 'Product strategy is highly viable and recommended for immediate implementation.',
                'confidence': 0.9,
                'risk_level': 'low',
                'roi_estimate': 0.18
            }
        elif product_strategy_score >= 0.6:
            recommendation = {
                'text': 'Product strategy is viable but requires additional preparation and resource allocation.',
                'confidence': 0.7,
                'risk_level': 'medium',
                'roi_estimate': 0.10
            }
        elif product_strategy_score >= 0.4:
            recommendation = {
                'text': 'Product strategy requires significant refinement. Review innovation and supply chain factors.',
                'confidence': 0.5,
                'risk_level': 'medium-high',
                'roi_estimate': 0.04
            }
        else:
            recommendation = {
                'text': 'Product strategy does not meet viability threshold. Recommend major revision.',
                'confidence': 0.4,
                'risk_level': 'high',
                'roi_estimate': -0.02
            }

        logger.debug(f"Product recommendation generated: confidence={recommendation['confidence']:.2f}")
        return recommendation

    def _generate_explanation(self, recommendation: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate LLM-based explanation (optional)

        Args:
            recommendation: Recommendation from deterministic logic
            analysis: Analysis results

        Returns:
            str: LLM-generated explanation
        """
        if not self.llm:
            return ""

        try:
            prompt = f"""
            Based on the following product strategy analysis, provide a brief (2-3 sentence) business explanation:

            Product Strategy Score: {analysis.get('product_strategy_score', 0):.2f}
            Innovation Score: {analysis.get('innovation_score', 0):.2f}
            Supply Chain Score: {analysis.get('supply_chain_score', 0):.2f}
            Recommendation: {recommendation.get('text', '')}

            Explanation:
            """

            explanation = self.llm.infer(prompt)
            logger.debug("LLM product strategy explanation generated")
            return explanation

        except Exception as e:
            logger.warning(f"Failed to generate LLM product strategy explanation: {e}")
            return ""

    def analyze(self, data: dict) -> dict:
        """Analyze product strategic information

        Args:
            data: Product strategic data to analyze

        Returns:
            dict: Analysis results
        """
        return self._analyze_product_strategy(data)

    def generate_plan(self, objectives: list) -> dict:
        """Generate product strategic plan

        Args:
            objectives: List of product strategic objectives

        Returns:
            dict: Product strategic plan
        """
        return {
            'plan_id': str(uuid.uuid4())[:8],
            'objectives': objectives,
            'actions': [f"Product action for objective: {obj}" for obj in objectives],
            'timeline': 'Q1-Q2',
            'success_metrics': ['Product adoption rate', 'Market share', 'Customer satisfaction']
        }
    """Agent responsible for strategic analysis and planning"""
    
    def __init__(self, config=None, llm=None):
        """Initialize StrategyAgent
        
        Args:
            config: Configuration object
            llm: Optional LLM for explanation generation
        """
        self.config = config
        self.llm = llm
        self.agent_type = AgentType.STRATEGY
    
    def process(self, decision_input: DecisionInput) -> StructuredDecision:
        """Process strategic decision request
        
        Args:
            decision_input: Input decision request
            
        Returns:
            StructuredDecision: Strategic decision
        """
        decision_id = str(uuid.uuid4())[:8]
        
        try:
            # Step 1: Extract strategic factors
            strategic_factors = self._extract_factors(decision_input.context)
            
            # Step 2: Perform strategic analysis
            analysis = self._analyze_strategy(strategic_factors)
            
            # Step 3: Generate recommendation
            recommendation = self._generate_recommendation(analysis)
            
            # Step 4: Generate explanation (if LLM available)
            explanation = ""
            if self.llm:
                explanation = self._generate_explanation(recommendation, analysis)
            
            # Step 5: Create decision
            decision = StructuredDecision(
                decision_id=decision_id,
                agent_used=self.agent_type,
                decision_text=recommendation.get('text', 'No recommendation'),
                confidence=recommendation.get('confidence', 0.5),
                risk_level=recommendation.get('risk_level', 'medium'),
                roi_estimate=recommendation.get('roi_estimate', 0.0),
                reasoning={
                    'factors': strategic_factors,
                    'analysis': analysis,
                    'explanation': explanation
                },
                validation_score=analysis.get('strategy_score', 0.5),
                status=DecisionStatus.PENDING
            )
            
            logger.info(f"Strategy decision {decision_id} generated (confidence: {decision.confidence:.2f})")
            return decision
        
        except Exception as e:
            logger.error(f"Strategy processing failed: {e}")
            raise
    
    def _extract_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract strategic factors from context
        
        Args:
            context: Decision context
            
        Returns:
            Dict with extracted strategic factors
        """
        factors = {
            'objectives': context.get('objectives', []),
            'constraints': context.get('constraints', []),
            'resources': context.get('resources', []),
            'timeline': context.get('timeline', ''),
            'stakeholders': context.get('stakeholders', []),
            'risk_tolerance': context.get('risk_tolerance', 'medium')
        }
        
        logger.debug(f"Extracted factors: {len(factors)} categories")
        return factors
    
    def _analyze_strategy(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Perform strategic analysis using deterministic rules
        
        Args:
            factors: Strategic factors
            
        Returns:
            Dict with analysis results
        """
        analysis = {
            'feasibility_score': 0.0,
            'alignment_score': 0.0,
            'resource_score': 0.0,
            'timeline_score': 0.0,
            'strategy_score': 0.0
        }
        
        # Feasibility assessment (0-1)
        num_objectives = len(factors.get('objectives', []))
        num_constraints = len(factors.get('constraints', []))
        analysis['feasibility_score'] = max(1.0 - (num_constraints / max(num_objectives, 1)) * 0.5, 0.0)
        
        # Resource alignment (0-1)
        num_resources = len(factors.get('resources', []))
        analysis['resource_score'] = min(num_resources / 3, 1.0)  # Assume 3 resources is optimal
        
        # Timeline assessment (0-1)
        timeline = factors.get('timeline', '')
        if timeline:
            # Simple heuristic: shorter timelines get lower scores
            timeline_lower = timeline.lower()
            if 'immediately' in timeline_lower or 'urgent' in timeline_lower:
                analysis['timeline_score'] = 0.6
            elif 'week' in timeline_lower:
                analysis['timeline_score'] = 0.8
            elif 'month' in timeline_lower or 'quarter' in timeline_lower:
                analysis['timeline_score'] = 0.9
            else:
                analysis['timeline_score'] = 0.7
        else:
            analysis['timeline_score'] = 0.5
        
        # Overall strategy score (weighted average)
        analysis['strategy_score'] = (
            analysis['feasibility_score'] * 0.35 +
            analysis['resource_score'] * 0.25 +
            analysis['timeline_score'] * 0.40
        )
        
        logger.debug(f"Strategy analysis: feasibility={analysis['feasibility_score']:.2f}, resource={analysis['resource_score']:.2f}, strategy={analysis['strategy_score']:.2f}")
        
        return analysis
    
    def _generate_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic recommendation
        
        Args:
            analysis: Analysis results
            
        Returns:
            Dict with recommendation
        """
        strategy_score = analysis.get('strategy_score', 0.5)
        
        # Deterministic recommendation rules
        if strategy_score >= 0.8:
            recommendation = {
                'text': 'Strategy is highly viable and recommended for immediate implementation.',
                'confidence': 0.9,
                'risk_level': 'low',
                'roi_estimate': 0.15
            }
        elif strategy_score >= 0.6:
            recommendation = {
                'text': 'Strategy is viable but requires additional preparation and resource allocation.',
                'confidence': 0.7,
                'risk_level': 'medium',
                'roi_estimate': 0.08
            }
        elif strategy_score >= 0.4:
            recommendation = {
                'text': 'Strategy requires significant refinement. Review constraints and objectives.',
                'confidence': 0.5,
                'risk_level': 'medium-high',
                'roi_estimate': 0.03
            }
        else:
            recommendation = {
                'text': 'Strategy does not meet viability threshold. Recommend major revision.',
                'confidence': 0.4,
                'risk_level': 'high',
                'roi_estimate': -0.05
            }
        
        logger.debug(f"Recommendation generated: confidence={recommendation['confidence']:.2f}")
        return recommendation
    
    def _generate_explanation(self, recommendation: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate LLM-based explanation (optional)
        
        Args:
            recommendation: Recommendation from deterministic logic
            analysis: Analysis results
            
        Returns:
            str: LLM-generated explanation
        """
        if not self.llm:
            return ""
        
        try:
            prompt = f"""
            Based on the following strategic analysis, provide a brief (2-3 sentence) business explanation:
            
            Strategy Score: {analysis.get('strategy_score', 0):.2f}
            Recommendation: {recommendation.get('text', '')}
            Risk Level: {recommendation.get('risk_level', '')}
            
            Explanation:
            """
            
            explanation = self.llm.infer(prompt)
            logger.debug("LLM explanation generated")
            return explanation
        
        except Exception as e:
            logger.warning(f"Failed to generate LLM explanation: {e}")
            return ""
    
    def analyze(self, data: dict) -> dict:
        """Analyze strategic information
        
        Args:
            data: Strategic data to analyze
            
        Returns:
            dict: Analysis results
        """
        return self._analyze_strategy(data)
    
    def generate_plan(self, objectives: list) -> dict:
        """Generate strategic plan
        
        Args:
            objectives: List of strategic objectives
            
        Returns:
            dict: Strategic plan
        """
        return {
            'plan_id': str(uuid.uuid4())[:8],
            'objectives': objectives,
            'actions': [f"Action for objective: {obj}" for obj in objectives],
            'timeline': 'Q1-Q2',
            'success_metrics': ['Revenue increase', 'Market share', 'Customer satisfaction']
        }
