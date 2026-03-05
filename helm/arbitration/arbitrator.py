"""Deterministic Arbitration Engine for HELM v3"""

from typing import Dict, Any

from ..schemas import StructuredDecision, AgentType
from ..config import Config


def clamp(value: float, minval: float = 0.0, maxval: float = 1.0) -> float:
    return max(min(value, maxval), minval)  # clamp value between minval and maxval


class ArbitrationEngine:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.weights = getattr(self.config, 'ARBITRATION_WEIGHTS', {
            'product_strategy': 0.25,
            'competitive_strategy': 0.20,
            'market_intelligence': 0.25,
            'finance_optimization': 0.30
        })
        # ensure weights sum to 1
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Arbitration weights must sum to 1, got {total}")
        self.risk_penalty_factor = getattr(self.config, 'RISK_PENALTY_FACTOR', 0.5)

    def compute(self, dec_a: StructuredDecision, dec_b: StructuredDecision) -> Dict[str, Any]:
        # determine which decision should be treated as strategy vs finance
        # prioritize explicit agent types, then deterministic score-based heuristics
        strat_dec = None
        fin_dec = None

        # explicit classification when agent_used is unambiguous
        if dec_a.agent_used == AgentType.FINANCE and dec_b.agent_used != AgentType.FINANCE:
            fin_dec, strat_dec = dec_a, dec_b
        elif dec_b.agent_used == AgentType.FINANCE and dec_a.agent_used != AgentType.FINANCE:
            fin_dec, strat_dec = dec_b, dec_a
        elif dec_a.agent_used == AgentType.STRATEGY and dec_b.agent_used != AgentType.STRATEGY:
            strat_dec, fin_dec = dec_a, dec_b
        elif dec_b.agent_used == AgentType.STRATEGY and dec_a.agent_used != AgentType.STRATEGY:
            strat_dec, fin_dec = dec_b, dec_a
        else:
            # ambiguous or both same type: use deterministic heuristics based on values
            # sort decisions by (roi_estimate, validation_score) descending
            pair = sorted(
                [dec_a, dec_b],
                key=lambda d: (getattr(d, 'roi_estimate', 0.0), getattr(d, 'validation_score', 0.0)),
                reverse=True
            )
            fin_dec, strat_dec = pair[0], pair[1]

        # extract necessary values
        strat_viability = getattr(strat_dec, 'validation_score', 0.0)
        roi = getattr(fin_dec, 'roi_estimate', 0.0)
        # compute risk score based on finance validation if present
        # default risk_score = 1 - finance validation_score
        risk_score = 1.0 - getattr(fin_dec, 'validation_score', 0.0)
        normalized_risk = clamp(risk_score, 0.0, 1.0)

        # risk-adjusted ROI
        risk_penalty = normalized_risk * self.risk_penalty_factor
        adjusted_roi = roi * (1 - risk_penalty)

        strat_component = self.weights['strategy'] * strat_viability
        fin_component = self.weights['finance'] * adjusted_roi
        composite = strat_component + fin_component

        confidence = 0.5 * (getattr(strat_dec, 'confidence', 0.0) + getattr(fin_dec, 'confidence', 0.0))
        dominant = 'strategy' if strat_component >= fin_component else 'finance'

        return {
            'composite_score': composite,
            'strategy_component': strat_component,
            'finance_component': fin_component,
            'risk_adjustment': risk_penalty,
            'dominant_factor': dominant,
            'confidence': confidence
        }

    def compute_multi(self, product_dec: StructuredDecision, competitive_dec: StructuredDecision, 
                     market_dec: StructuredDecision, finance_dec: StructuredDecision) -> Dict[str, Any]:
        """Compute arbitration for 4 agents: product, competitive, market, finance"""
        # Extract scores
        product_score = getattr(product_dec, 'validation_score', 0.0)
        competitive_score = getattr(competitive_dec, 'validation_score', 0.0)
        market_score = getattr(market_dec, 'validation_score', 0.0)
        finance_score = getattr(finance_dec, 'validation_score', 0.0)
        
        # Calculate risk score based on variance between agents
        scores = [product_score, competitive_score, market_score, finance_score]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        risk_score = min(variance * 2, 1.0)  # Scale variance to 0-1 risk score
        normalized_risk = clamp(risk_score, 0.0, 1.0)
        
        # Risk-adjusted scores
        risk_penalty = normalized_risk * self.risk_penalty_factor
        adjusted_product = product_score * (1 - risk_penalty * 0.5)  # Less penalty for product
        adjusted_competitive = competitive_score * (1 - risk_penalty * 0.7)  # More penalty for competitive
        adjusted_market = market_score * (1 - risk_penalty * 0.6)
        adjusted_finance = finance_score * (1 - risk_penalty)  # Full penalty for finance
        
        # Weighted components
        product_component = self.weights['product_strategy'] * adjusted_product
        competitive_component = self.weights['competitive_strategy'] * adjusted_competitive
        market_component = self.weights['market_intelligence'] * adjusted_market
        finance_component = self.weights['finance_optimization'] * adjusted_finance
        
        composite = product_component + competitive_component + market_component + finance_component
        
        # Determine dominant factor
        components = {
            'product_strategy': product_component,
            'competitive_strategy': competitive_component,
            'market_intelligence': market_component,
            'finance_optimization': finance_component
        }
        dominant = max(components, key=components.get)
        
        # Overall confidence based on score consistency and magnitude
        confidence = (
            0.4 * (1 - normalized_risk) +  # Consistency bonus
            0.6 * clamp(composite, 0.0, 1.0)  # Score magnitude
        )
        
        return {
            'composite_score': composite,
            'product_component': product_component,
            'competitive_component': competitive_component,
            'market_component': market_component,
            'finance_component': finance_component,
            'risk_adjustment': risk_penalty,
            'score_variance': variance,
            'dominant_factor': dominant,
            'confidence': confidence,
            'agent_scores': {
                'product_strategy': product_score,
                'competitive_strategy': competitive_score,
                'market_intelligence': market_score,
                'finance_optimization': finance_score
            }
        }
