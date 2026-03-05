"""
Market Intelligence Agent - Handles market analysis and intelligence gathering
Deterministic market analysis and demand forecasting
"""

import logging
import uuid
from typing import Dict, Any

from ..schemas import (
    AgentType, DecisionStatus, StructuredDecision, DecisionInput
)


logger = logging.getLogger(__name__)


class MarketIntelligenceAgent:
    """Agent responsible for market intelligence and analysis"""

    def __init__(self, config=None, llm=None):
        """Initialize MarketIntelligenceAgent

        Args:
            config: Configuration object
            llm: Optional LLM for explanation generation
        """
        self.config = config
        self.llm = llm
        self.agent_type = AgentType.MARKET_INTELLIGENCE

    def process(self, decision_input: DecisionInput) -> StructuredDecision:
        """Process market intelligence decision request

        Args:
            decision_input: Input decision request

        Returns:
            StructuredDecision: Market intelligence decision
        """
        decision_id = str(uuid.uuid4())[:8]

        try:
            # Step 1: Extract market intelligence factors
            market_factors = self._extract_factors(decision_input.context)

            # Step 2: Perform market intelligence analysis
            analysis = self._analyze_market_intelligence(market_factors)

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
                    'factors': market_factors,
                    'analysis': analysis,
                    'explanation': explanation
                },
                validation_score=analysis.get('market_intelligence_score', 0.5),
                status=DecisionStatus.PENDING
            )

            logger.info(f"Market intelligence decision {decision_id} generated (confidence: {decision.confidence:.2f})")
            return decision

        except Exception as e:
            logger.error(f"Market intelligence processing failed: {e}")
            raise

    def _extract_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market intelligence factors from context

        Args:
            context: Decision context

        Returns:
            Dict with extracted market intelligence factors
        """
        factors = {
            'market_growth': context.get('market_growth', 0.5),
            'demand_index': context.get('demand_index', 0.5),
            'competitor_strength': context.get('competitor_strength', 0.5),
            'product_innovation': context.get('product_innovation', 0.5),
            'supply_chain_efficiency': context.get('supply_chain_efficiency', 0.5),
            'economic_indicators': context.get('economic_indicators', {}),
            'regulatory_environment': context.get('regulatory_environment', 'neutral')
        }

        logger.debug(f"Extracted market factors: {len(factors)} categories")
        return factors

    def _analyze_market_intelligence(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Perform market intelligence analysis using deterministic rules

        Args:
            factors: Market intelligence factors

        Returns:
            Dict with analysis results
        """
        analysis = {
            'market_growth_score': 0.0,
            'demand_score': 0.0,
            'competition_score': 0.0,
            'innovation_score': 0.0,
            'supply_chain_score': 0.0,
            'regulatory_score': 0.0,
            'market_intelligence_score': 0.0
        }

        # Market growth score (0-1)
        market_growth = factors.get('market_growth', 0.5)
        analysis['market_growth_score'] = min(max(market_growth, 0.0), 1.0)

        # Demand index score (0-1)
        demand_index = factors.get('demand_index', 0.5)
        analysis['demand_score'] = min(max(demand_index, 0.0), 1.0)

        # Competition score (inverse of competitor strength)
        competitor_strength = factors.get('competitor_strength', 0.5)
        analysis['competition_score'] = 1.0 - min(max(competitor_strength, 0.0), 1.0)

        # Innovation score (0-1)
        innovation = factors.get('product_innovation', 0.5)
        analysis['innovation_score'] = min(max(innovation, 0.0), 1.0)

        # Supply chain efficiency score (0-1)
        supply_chain = factors.get('supply_chain_efficiency', 0.5)
        analysis['supply_chain_score'] = min(max(supply_chain, 0.0), 1.0)

        # Regulatory environment score (0-1)
        regulatory = factors.get('regulatory_environment', 'neutral').lower()
        if regulatory == 'favorable':
            analysis['regulatory_score'] = 0.9
        elif regulatory == 'neutral':
            analysis['regulatory_score'] = 0.6
        elif regulatory == 'challenging':
            analysis['regulatory_score'] = 0.3
        else:
            analysis['regulatory_score'] = 0.5

        # Overall market intelligence score (weighted average)
        analysis['market_intelligence_score'] = (
            analysis['market_growth_score'] * 0.20 +
            analysis['demand_score'] * 0.20 +
            analysis['competition_score'] * 0.15 +
            analysis['innovation_score'] * 0.15 +
            analysis['supply_chain_score'] * 0.15 +
            analysis['regulatory_score'] * 0.15
        )

        logger.debug(f"Market intelligence analysis: growth={analysis['market_growth_score']:.2f}, demand={analysis['demand_score']:.2f}, market_intelligence={analysis['market_intelligence_score']:.2f}")

        return analysis

    def _generate_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market intelligence recommendation

        Args:
            analysis: Analysis results

        Returns:
            Dict with recommendation
        """
        market_intelligence_score = analysis.get('market_intelligence_score', 0.5)

        # Deterministic recommendation rules
        if market_intelligence_score >= 0.8:
            recommendation = {
                'text': 'Market conditions are highly favorable with strong growth potential.',
                'confidence': 0.9,
                'risk_level': 'low',
                'roi_estimate': 0.22
            }
        elif market_intelligence_score >= 0.6:
            recommendation = {
                'text': 'Market conditions are favorable but require monitoring of key indicators.',
                'confidence': 0.7,
                'risk_level': 'medium',
                'roi_estimate': 0.14
            }
        elif market_intelligence_score >= 0.4:
            recommendation = {
                'text': 'Market conditions are mixed. Consider additional market research.',
                'confidence': 0.5,
                'risk_level': 'medium-high',
                'roi_estimate': 0.06
            }
        else:
            recommendation = {
                'text': 'Market conditions are unfavorable. High risk of poor performance.',
                'confidence': 0.4,
                'risk_level': 'high',
                'roi_estimate': 0.01
            }

        logger.debug(f"Market intelligence recommendation generated: confidence={recommendation['confidence']:.2f}")
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
            Based on the following market intelligence analysis, provide a brief (2-3 sentence) business explanation:

            Market Intelligence Score: {analysis.get('market_intelligence_score', 0):.2f}
            Market Growth: {analysis.get('market_growth_score', 0):.2f}
            Demand Index: {analysis.get('demand_score', 0):.2f}
            Competition: {analysis.get('competition_score', 0):.2f}
            Recommendation: {recommendation.get('text', '')}

            Explanation:
            """

            explanation = self.llm.infer(prompt)
            logger.debug("LLM market intelligence explanation generated")
            return explanation

        except Exception as e:
            logger.warning(f"Failed to generate LLM market intelligence explanation: {e}")
            return ""

    def analyze(self, data: dict) -> dict:
        """Analyze market intelligence information

        Args:
            data: Market intelligence data to analyze

        Returns:
            dict: Analysis results
        """
        return self._analyze_market_intelligence(data)

    def forecast_demand(self, market_data: dict) -> dict:
        """Forecast market demand

        Args:
            market_data: Market data for forecasting

        Returns:
            dict: Demand forecast
        """
        return {
            'forecast_id': str(uuid.uuid4())[:8],
            'current_demand': market_data.get('demand_index', 0.5),
            'projected_growth': market_data.get('market_growth', 0.5),
            'confidence': 0.7,
            'time_horizon': '12 months'
        }