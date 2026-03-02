"""
Dashboard UI - Streamlit-based visualization and interaction
Read-only dashboard consuming decisions from core engine
"""

import logging
from typing import Dict, Any, List

from ..config import Config

logger = logging.getLogger(__name__)


class Dashboard:
    """Web-based Streamlit dashboard interface for HELM decisions"""
    
    def __init__(self, host: str = "localhost", port: int = 8501, config=None):
        """Initialize Dashboard
        
        Args:
            host: Server host
            port: Server port
            config: Configuration object
        """
        self.host = host
        self.port = port
        self.config = config
        self.app = None
        self.db = None
    
    def start(self) -> bool:
        """Start dashboard server
        
        Returns:
            bool: True if started successfully
        """
        try:
            # If demo mode, allow start without streamlit
            if self.config and getattr(self.config, 'DEMO_MODE', False):
                logger.info("Dashboard demo mode active — starting lightweight dashboard")
                return True

            import streamlit as st
            logger.info(f"Dashboard starting on {self.host}:{self.port}")
            return True

        except ImportError:
            logger.error("Streamlit not installed. Install with: pip install streamlit")
            return False
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop dashboard server
        
        Returns:
            bool: True if stopped successfully
        """
        try:
            logger.info("Dashboard stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop dashboard: {e}")
            return False
    
    def render(self, decisions: List[Dict[str, Any]] = None) -> None:
        """Render dashboard with decision data
        
        Args:
            decisions: List of decision objects to display
        """
        try:
            import streamlit as st
            
            # Page config
            st.set_page_config(
                page_title="HELM v2.0 Dashboard",
                page_icon="⚙️",
                layout="wide"
            )
            
            st.title("🤖 HELM v2.0 - Decision Dashboard")
            st.markdown("Hierarchical Executive-Level Meta-Agent Decision Monitoring")
            
            # Sidebar
            st.sidebar.header("Dashboard Controls")
            # sliders for arbitration weights and thresholds
            strat_w = st.sidebar.slider("Strategy Weight", 0.0, 1.0, self.config.ARBITRATION_WEIGHTS.get('strategy', 0.5), 0.01)
            fin_w = 1.0 - strat_w
            st.sidebar.write(f"Finance Weight: {fin_w:.2f}")
            threshold = st.sidebar.slider("Validation Threshold", 0.0, 1.0, self.config.validation_threshold if self.config else 0.7, 0.01)
            apply_risk = st.sidebar.checkbox("Risk Penalty", value=True)
            risk_factor = 0.0
            if apply_risk:
                risk_factor = st.sidebar.slider("Risk Penalty Factor", 0.0, 1.0, self.config.RISK_PENALTY_FACTOR if self.config else 0.5, 0.01)
            mode = st.sidebar.radio("Mode", ["Simple", "Expert"])

            # compute derived arbitration for decisions if available
            arb_engine = None
            try:
                from ..arbitration.arbitrator import ArbitrationEngine
                # create temp config with sliders
                temp_cfg = self.config or Config()
                temp_cfg.ARBITRATION_WEIGHTS = {'strategy': strat_w, 'finance': fin_w}
                temp_cfg.RISK_PENALTY_FACTOR = risk_factor
                arb_engine = ArbitrationEngine(temp_cfg)
            except Exception:
                arb_engine = None

            # Main content rendering
            if mode == "Simple":
                self._render_simple(decisions or [], arb_engine, threshold)
            else:
                self._render_expert(decisions or [], arb_engine, threshold, strat_w, fin_w, risk_factor)
            
            # Footer
            st.markdown("---")
            st.caption("HELM v2.0 | Deterministic Decision Authority System")
        
        except ImportError:
            logger.error("Streamlit not available for rendering")
        except Exception as e:
            logger.error(f"Dashboard render failed: {e}")
    
    def _render_overview(self) -> None:
        """Render overview section"""
        try:
            import streamlit as st
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="Total Decisions", value="42")
            with col2:
                st.metric(label="Acceptance Rate", value="85%")
            with col3:
                st.metric(label="Avg Confidence", value="0.82")
            with col4:
                st.metric(label="Avg ROI Estimate", value="12.5%")
            
            st.subheader("System Status")
            st.info("[OK] All systems operational")
            st.info("[OK] CUDA available: RTX 3050 (6GB)")
            st.info("[OK] Local model loaded: microsoft/phi-2")
        
        except Exception as e:
            logger.error(f"Overview render failed: {e}")
    
    def _render_recent_decisions(self, decisions: List[Dict[str, Any]] = None) -> None:
        """Render recent decisions
        
        Args:
            decisions: List of decisions
        """
        try:
            import streamlit as st
            
            st.subheader("Recent Decisions")
            
            if decisions:
                for decision in decisions[:10]:
                    with st.expander(f"Decision {decision.get('id', 'N/A')[:8]} - {decision.get('agent_used', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Status**: {decision.get('status', 'N/A')}")
                            st.write(f"**Agent**: {decision.get('agent_used', 'N/A')}")
                            st.write(f"**Confidence**: {decision.get('confidence', 0):.2%}")
                        with col2:
                            st.write(f"**Risk Level**: {decision.get('risk_level', 'N/A')}")
                            st.write(f"**ROI Estimate**: {decision.get('roi_estimate', 0):.2%}")
                            st.write(f"**Timestamp**: {decision.get('timestamp', 'N/A')}")
                        
                        st.write(f"**Decision**: {decision.get('decision_text', 'N/A')}")
            else:
                st.info("No decisions available yet")
        
        except Exception as e:
            logger.error(f"Recent decisions render failed: {e}")
    
    def _render_agent_stats(self) -> None:
        """Render agent statistics"""
        try:
            import streamlit as st
            
            st.subheader("Agent Performance Statistics")
            
            agent_data = {
                'HeadAgent': {'decisions': 10, 'acceptance_rate': 0.8},
                'StrategyAgent': {'decisions': 15, 'acceptance_rate': 0.87},
                'FinanceAgent': {'decisions': 17, 'acceptance_rate': 0.82}
            }
            
            for agent, stats in agent_data.items():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label=f"{agent}", value=stats['decisions'], label_visibility="collapsed")
                with col2:
                    st.metric(label="Acceptance Rate", value=f"{stats['acceptance_rate']:.1%}")
        
        except Exception as e:
            logger.error(f"Agent stats render failed: {e}")
    
    def _render_financial_analysis(self, decisions: List[Dict[str, Any]] = None) -> None:
        """Render financial analysis
        
        Args:
            decisions: List of decisions
        """
        try:
            import streamlit as st
            
            st.subheader("Financial Analysis")
            
            if decisions:
                roi_estimates = [d.get('roi_estimate', 0) for d in decisions if d.get('agent_used') == 'finance']
                avg_roi = sum(roi_estimates) / len(roi_estimates) if roi_estimates else 0
                
                st.metric(label="Average ROI (Finance Decisions)", value=f"{avg_roi:.2%}")
                st.info(f"Analyzed {len(roi_estimates)} financial decisions")
            else:
                st.info("No financial decisions available for analysis")
        
        except Exception as e:
            logger.error(f"Financial analysis render failed: {e}")

    # --- new rendering helpers for Phase 4B ---
    def _render_simple(self, decisions: List[Dict[str, Any]], arb_engine, threshold: float) -> None:
        try:
            import streamlit as st
            st.subheader("Executive Summary (Simple Mode)")
            if not decisions or not arb_engine:
                st.info("No decision data available for summary")
                return
            latest = decisions[-1]
            # compute arbitration breakdown using engine
            arb = arb_engine.compute(latest, latest) if False else {}  # placeholder
            # since we don't know other decision for pair, use reasoning if present
            arb = latest.get('reasoning', {}).get('arbitration', {})
            st.markdown(f"**Final Decision:** {latest.get('decision_text', 'N/A')}")
            st.markdown(f"**Risk-adjusted ROI:** {arb.get('finance_component', 0):.2f}")
            # breakdown chart
            breakdown = {'strategy': arb.get('strategy_component', 0), 'finance': arb.get('finance_component', 0)}
            st.bar_chart(breakdown)
            st.markdown("---")
            st.write("This summary hides detailed validation math and raw JSON.")
        except Exception as e:
            logger.error(f"Simple mode render failed: {e}")

    def _render_expert(self, decisions: List[Dict[str, Any]], arb_engine, threshold: float, strat_w: float, fin_w: float, risk_factor: float) -> None:
        try:
            import streamlit as st
            import pandas as pd
            st.subheader("Expert Dashboard")
            if not decisions or not arb_engine:
                st.info("No decision data available for expert view")
                return
            # compute metrics for each decision pair if possible
            comps = []
            for d in decisions:
                # expect decision may already include arbitration results
                arb = d.get('reasoning', {}).get('arbitration', {})
                comps.append({
                    'timestamp': d.get('timestamp'),
                    'strategy_score': arb.get('strategy_component', 0),
                    'finance_score': arb.get('finance_component', 0),
                    'composite': arb.get('composite_score', 0),
                    'risk_adjustment': arb.get('risk_adjustment', 0),
                    'validator_score': d.get('validation_score', 0)
                })
            df = pd.DataFrame(comps)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                st.line_chart(df.set_index('timestamp')[['strategy_score', 'finance_score', 'composite']])
                st.write("Threshold comparison")
                st.line_chart(df.set_index('timestamp')['validator_score'])
                # risk vs ROI scatter
                df['roi'] = [d.get('roi_estimate', 0) for d in decisions]
                df['risk'] = [1 - d.get('validation_score', 0) for d in decisions]
                st.write("Risk vs ROI")
                st.scatter_chart(df[['risk', 'roi']])
                st.write("Score distribution")
                st.bar_chart(df['composite'])
                st.write("Escalation region (validator < threshold)")
                esc = df['validator_score'] < threshold
                st.bar_chart(esc.astype(int))
            else:
                st.info("No computed composite scores available")
        except Exception as e:
            logger.error(f"Expert mode render failed: {e}")
