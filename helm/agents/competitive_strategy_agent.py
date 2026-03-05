"""
Competitive Strategy Agent - Handles competitive analysis and market positioning
Deterministic strategic reasoning for competitive advantage
"""

import logging
import uuid
from typing import Dict, Any

from ..schemas import (
    AgentType, DecisionStatus, StructuredDecision, DecisionInput
)


logger = logging.getLogger(__name__)


class CompetitiveStrategyAgent:
    """Agent responsible for competitive strategic analysis and positioning"""

    def __init__(self, config=None, llm=None):
        """Initialize CompetitiveStrategyAgent

        Args:
            config: Configuration object
            llm: Optional LLM for explanation generation
        """
        self.config = config
        self.llm = llm
        self.agent_type = AgentType.COMPETITIVE_STRATEGY

    def process(self, decision_input: DecisionInput) -> StructuredDecision:
        """Process competitive strategy decision request

        Args:
            decision_input: Input decision request

        Returns:
            StructuredDecision: Competitive strategy decision
        """
        decision_id = str(uuid.uuid4())[:8]

        try:
            # Step 1: Extract competitive strategic factors
            competitive_factors = self._extract_factors(decision_input.context)

            # Step 2: Perform competitive strategy analysis
            analysis = self._analyze_competitive_strategy(competitive_factors)

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
                    'factors': competitive_factors,
                    'analysis': analysis,
                    'explanation': explanation
                },
                validation_score=analysis.get('competitive_strategy_score', 0.5),
                status=DecisionStatus.PENDING
            )

            logger.info(f"Competitive strategy decision {decision_id} generated (confidence: {decision.confidence:.2f})")
            return decision

        except Exception as e:
            logger.error(f"Competitive strategy processing failed: {e}")
            raise

    def _extract_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competitive strategic factors from context

        Args:
            context: Decision context

        Returns:
            Dict with extracted competitive strategic factors
        """
        factors = {
            'objectives': context.get('objectives', []),
            'constraints': context.get('constraints', []),
            'resources': context.get('resources', []),
            'timeline': context.get('timeline', ''),
            'stakeholders': context.get('stakeholders', []),
            'risk_tolerance': context.get('risk_tolerance', 'medium'),
            'competitor_strength': context.get('competitor_strength', 0.5),
            'market_growth': context.get('market_growth', 0.5)
        }

        logger.debug(f"Extracted competitive factors: {len(factors)} categories")
        return factors

    def _analyze_competitive_strategy(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Perform competitive strategy analysis using deterministic rules

        Args:
            factors: Competitive strategic factors

        Returns:
            Dict with analysis results
        """
        analysis = {
            'feasibility_score': 0.0,
            'alignment_score': 0.0,
            'resource_score': 0.0,
            'timeline_score': 0.0,
            'competitor_score': 0.0,
            'market_score': 0.0,
            'competitive_strategy_score': 0.0
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

        # Competitor strength score (inverse - lower competitor strength is better)
        competitor_strength = factors.get('competitor_strength', 0.5)
        analysis['competitor_score'] = 1.0 - min(max(competitor_strength, 0.0), 1.0)

        # Market growth score (0-1)
        market_growth = factors.get('market_growth', 0.5)
        analysis['market_score'] = min(max(market_growth, 0.0), 1.0)

        # Overall competitive strategy score (weighted average)
        analysis['competitive_strategy_score'] = (
            analysis['feasibility_score'] * 0.20 +
            analysis['resource_score'] * 0.15 +
            analysis['timeline_score'] * 0.15 +
            analysis['competitor_score'] * 0.25 +
            analysis['market_score'] * 0.25
        )

        logger.debug(f"Competitive strategy analysis: competitor={analysis['competitor_score']:.2f}, market={analysis['market_score']:.2f}, competitive_strategy={analysis['competitive_strategy_score']:.2f}")

        return analysis

    def _generate_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate competitive strategy recommendation

        Args:
            analysis: Analysis results

        Returns:
            Dict with recommendation
        """
        competitive_strategy_score = analysis.get('competitive_strategy_score', 0.5)

        # Deterministic recommendation rules
        if competitive_strategy_score >= 0.8:
            recommendation = {
                'text': 'Competitive strategy is highly viable with strong market positioning potential.',
                'confidence': 0.9,
                'risk_level': 'low',
                'roi_estimate': 0.20
            }
        elif competitive_strategy_score >= 0.6:
            recommendation = {
                'text': 'Competitive strategy is viable but requires monitoring of competitor actions.',
                'confidence': 0.7,
                'risk_level': 'medium',
                'roi_estimate': 0.12
            }
        elif competitive_strategy_score >= 0.4:
            recommendation = {
                'text': 'Competitive strategy requires significant refinement. Review market conditions.',
                'confidence': 0.5,
                'risk_level': 'medium-high',
                'roi_estimate': 0.05
            }
        else:
            recommendation = {
                'text': 'Competitive strategy does not meet viability threshold. Market conditions unfavorable.',
                'confidence': 0.4,
                'risk_level': 'high',
                'roi_estimate': -0.01
            }

        logger.debug(f"Competitive recommendation generated: confidence={recommendation['confidence']:.2f}")
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
            Based on the following competitive strategy analysis, provide a brief (2-3 sentence) business explanation:

            Competitive Strategy Score: {analysis.get('competitive_strategy_score', 0):.2f}
            Competitor Strength: {1 - analysis.get('competitor_score', 0):.2f}
            Market Growth: {analysis.get('market_score', 0):.2f}
            Recommendation: {recommendation.get('text', '')}

            Explanation:
            """

            explanation = self.llm.infer(prompt)
            logger.debug("LLM competitive strategy explanation generated")
            return explanation

        except Exception as e:
            logger.warning(f"Failed to generate LLM competitive strategy explanation: {e}")
            return ""

    def analyze(self, data: dict) -> dict:
        """Analyze competitive strategic information

        Args:
            data: Competitive strategic data to analyze

        Returns:
            dict: Analysis results
        """
        return self._analyze_competitive_strategy(data)

    def generate_plan(self, objectives: list) -> dict:
        """Generate competitive strategic plan

        Args:
            objectives: List of competitive strategic objectives

        Returns:
            dict: Competitive strategic plan
        """
        return {
            'plan_id': str(uuid.uuid4())[:8],
            'objectives': objectives,
            'actions': [f"Competitive action for objective: {obj}" for obj in objectives],
            'timeline': 'Q1-Q2',
            'success_metrics': ['Market share gain', 'Competitor displacement', 'Revenue growth']
        }