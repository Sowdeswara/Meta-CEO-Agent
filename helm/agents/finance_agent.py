"""
Finance Optimization Agent - Handles financial analysis and optimization
Deterministic financial metrics and ROI calculations
"""

import logging
import uuid
from typing import Dict, Any

from ..schemas import (
    AgentType, DecisionStatus, StructuredDecision, DecisionInput
)


logger = logging.getLogger(__name__)


class FinanceOptimizationAgent:
    """Agent responsible for financial analysis and calculations"""
    
    def __init__(self, config=None, llm=None):
        """Initialize FinanceAgent
        
        Args:
            config: Configuration object
            llm: Optional LLM for explanation generation
        """
        self.config = config
        self.llm = llm
        self.agent_type = AgentType.FINANCE_OPTIMIZATION
    
    def process(self, decision_input: DecisionInput) -> StructuredDecision:
        """Process financial decision request
        
        Args:
            decision_input: Input decision request
            
        Returns:
            StructuredDecision: Financial decision
        """
        decision_id = str(uuid.uuid4())[:8]
        
        try:
            # Step 1: Extract financial data
            financial_data = self._extract_financial_data(decision_input.context)
            
            # Step 2: Calculate financial metrics
            metrics = self._calculate_metrics(financial_data)
            
            # Step 3: Generate recommendation
            recommendation = self._generate_recommendation(metrics)
            
            # Step 4: Generate explanation (if LLM available)
            explanation = ""
            if self.llm:
                explanation = self._generate_explanation(recommendation, metrics)
            
            # Step 5: Create decision
            decision = StructuredDecision(
                decision_id=decision_id,
                agent_used=self.agent_type,
                decision_text=recommendation.get('text', 'No recommendation'),
                confidence=recommendation.get('confidence', 0.5),
                risk_level=recommendation.get('risk_level', 'medium'),
                roi_estimate=recommendation.get('roi_estimate', 0.0),
                reasoning={
                    'financials': financial_data,
                    'metrics': metrics,
                    'explanation': explanation
                },
                validation_score=metrics.get('overall_score', 0.5),
                status=DecisionStatus.PENDING
            )
            
            logger.info(f"Financial decision {decision_id} generated (ROI: {recommendation.get('roi_estimate', 0):.2%})")
            return decision
        
        except Exception as e:
            logger.error(f"Finance processing failed: {e}")
            raise
    
    def _extract_financial_data(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Extract financial data from context
        
        Args:
            context: Decision context
            
        Returns:
            Dict with financial data
        """
        financial_data = {
            'revenue': self._safe_float(context.get('revenue', 0)),
            'costs': self._safe_float(context.get('costs', 0)),
            'investment': self._safe_float(context.get('investment', 0)),
            'expected_returns': self._safe_float(context.get('expected_returns', 0)),
            'timeframe_years': self._safe_float(context.get('timeframe_years', 1))
        }
        
        logger.debug(f"Extracted financial data: {financial_data}")
        return financial_data
    
    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float
        
        Args:
            value: Value to convert
            
        Returns:
            float: Converted value or 0.0
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_metrics(self, financial_data: Dict[str, float]) -> Dict[str, float]:
        """Calculate financial metrics using deterministic formulas
        
        Args:
            financial_data: Financial data
            
        Returns:
            Dict with calculated metrics
        """
        metrics = {}
        
        # Extract values
        revenue = financial_data.get('revenue', 0)
        costs = financial_data.get('costs', 0)
        investment = financial_data.get('investment', 0)
        expected_returns = financial_data.get('expected_returns', 0)
        timeframe = financial_data.get('timeframe_years', 1)
        
        # 1. Profit Margin
        metrics['profit_margin'] = (revenue - costs) / revenue if revenue > 0 else 0
        metrics['profit_margin'] = max(min(metrics['profit_margin'], 1.0), -1.0)
        
        # 2. Return on Investment (ROI)
        metrics['roi'] = (expected_returns - investment) / investment if investment > 0 else 0
        
        # 3. Annualized ROI
        metrics['annualized_roi'] = ((1 + metrics['roi']) ** (1 / max(timeframe, 1)) - 1) if investment > 0 else 0
        
        # 4. Payback Period (years)
        if metrics['roi'] > 0 and investment > 0:
            annual_return = expected_returns / max(timeframe, 1)
            metrics['payback_period'] = investment / annual_return if annual_return > 0 else float('inf')
        else:
            metrics['payback_period'] = float('inf')
        
        # 5. Break-even analysis
        if revenue > 0 and costs > 0:
            metrics['contribution_margin'] = (revenue - costs) / revenue
        else:
            metrics['contribution_margin'] = 0
        
        # 6. Financial viability score (0-1)
        viability_factors = []
        
        # Positive profit margin
        if metrics['profit_margin'] > 0:
            viability_factors.append(0.3)
        elif metrics['profit_margin'] > -0.1:
            viability_factors.append(0.15)
        else:
            viability_factors.append(0.0)
        
        # Positive ROI
        if metrics['roi'] > 0:
            viability_factors.append(0.3)
        elif metrics['roi'] > -0.2:
            viability_factors.append(0.15)
        else:
            viability_factors.append(0.0)
        
        # Reasonable payback period
        if metrics['payback_period'] < float('inf') and metrics['payback_period'] <= 3:
            viability_factors.append(0.2)
        elif metrics['payback_period'] < float('inf') and metrics['payback_period'] <= 5:
            viability_factors.append(0.1)
        else:
            viability_factors.append(0.0)
        
        # Positive contribution
        if metrics['contribution_margin'] > 0.2:
            viability_factors.append(0.2)
        elif metrics['contribution_margin'] > 0:
            viability_factors.append(0.1)
        else:
            viability_factors.append(0.0)
        
        metrics['overall_score'] = sum(viability_factors) / len(viability_factors) if viability_factors else 0.5
        
        logger.debug(f"Calculated metrics: ROI={metrics['roi']:.2%}, Margin={metrics['profit_margin']:.2%}, Score={metrics['overall_score']:.2f}")
        
        return metrics
    
    def _generate_recommendation(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate financial recommendation based on metrics
        
        Args:
            metrics: Calculated financial metrics
            
        Returns:
            Dict with recommendation
        """
        score = metrics.get('overall_score', 0.5)
        roi = metrics.get('annualized_roi', 0)
        
        # Deterministic recommendation rules
        if score >= 0.7 and roi > 0.15:
            recommendation = {
                'text': 'Strong financial viability. Recommend proceeding with investment.',
                'confidence': 0.9,
                'risk_level': 'low',
                'roi_estimate': roi
            }
        elif score >= 0.5 and roi > 0.05:
            recommendation = {
                'text': 'Moderate financial viability. Proceed with caution and additional due diligence.',
                'confidence': 0.7,
                'risk_level': 'medium',
                'roi_estimate': roi
            }
        elif score >= 0.3:
            recommendation = {
                'text': 'Weak financial outlook. Recommend negotiating better terms or reconsidering.',
                'confidence': 0.5,
                'risk_level': 'medium-high',
                'roi_estimate': roi
            }
        else:
            recommendation = {
                'text': 'Poor financial metrics. Not recommended at current terms.',
                'confidence': 0.4,
                'risk_level': 'high',
                'roi_estimate': roi
            }
        
        logger.debug(f"Financial recommendation: {recommendation['text']}")
        return recommendation
    
    def _generate_explanation(self, recommendation: Dict[str, Any], metrics: Dict[str, float]) -> str:
        """Generate LLM-based financial explanation
        
        Args:
            recommendation: Recommendation from deterministic logic
            metrics: Calculated metrics
            
        Returns:
            str: LLM-generated explanation
        """
        if not self.llm:
            return ""
        
        try:
            prompt = f"""
            Explain in 2-3 sentences why this financial opportunity should be considered:
            
            ROI: {metrics.get('annualized_roi', 0):.2%}
            Profit Margin: {metrics.get('profit_margin', 0):.2%}
            Payback Period: {metrics.get('payback_period', float('inf')):.1f} years
            Overall Score: {metrics.get('overall_score', 0):.2f}/1.0
            
            Recommendation: {recommendation.get('text', '')}
            
            Explanation:
            """
            
            explanation = self.llm.infer(prompt)
            logger.debug("Financial LLM explanation generated")
            return explanation
        
        except Exception as e:
            logger.warning(f"Failed to generate financial explanation: {e}")
            return ""
    
    def analyze_financials(self, data: dict) -> dict:
        """Analyze financial data
        
        Args:
            data: Financial data to analyze
            
        Returns:
            dict: Analysis results
        """
        return self._calculate_metrics(data)
    
    def calculate_metrics(self, financials: dict) -> dict:
        """Calculate financial metrics
        
        Args:
            financials: Financial data
            
        Returns:
            dict: Calculated metrics
        """
        return self._calculate_metrics(financials)
