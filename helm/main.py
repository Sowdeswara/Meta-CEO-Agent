"""
HELM v2.0 - Application Entry Point
Complete system orchestration and decision authority
"""

import logging

from .config import Config
from .environment.system_check import SystemCheck
from .validation.validator import Validator
from .agents.head_agent import HeadAgent
from .agents.strategy_agent import StrategyAgent
from .agents.finance_agent import FinanceAgent
from .models.local_model import LocalModel
from .models.api_model import APIModel
from .schemas import DecisionInput, ModelConfig, AgentType
from .storage.database import Database
# The Streamlit-based dashboard has been removed. Import dynamically
# if dashboard functionality is required to avoid hard dependency.


logger = logging.getLogger(__name__)


class HELM:
    """HELM v2.0 - Hierarchical Executive-Level Meta-Agent System"""
    
    def __init__(self, enable_local_model: bool = True, enable_dashboard: bool = False, skip_system_check: bool = False, config: Config = None, local_model=None, api_model=None):
        """Initialize HELM system
        
        Args:
            enable_local_model: Use local model for explanations
            enable_dashboard: Enable Streamlit dashboard
            skip_system_check: When True, bypass environment validation (useful for testing)
        """
        logger.info("=" * 60)
        logger.info("HELM v2.0 - Initialization Started")
        logger.info("=" * 60)
        
        # 1. Load configuration (allow injection for tests)
        self.config = config or Config()
        logger.info("[OK] Configuration loaded")
        # 2. Perform system checks (required in production)
        env_status = None
        if skip_system_check and not self.config.DEVELOPMENT_MODE:
            raise RuntimeError("skip_system_check is only permitted when DEVELOPMENT_MODE is True")

        if not skip_system_check:
            system_check = SystemCheck()
            # In production we want errors to be raised for missing critical deps
            all_ok, env_status = system_check.check_environment(raise_on_missing=True)
            if not all_ok:
                logger.error("System checks failed!")
                logger.error(f"Environment status: {env_status.to_dict() if env_status else 'Unknown'}")
                raise RuntimeError("System environment check failed")
        else:
            logger.warning("Skipping system environment check because DEVELOPMENT_MODE is True")
        
        logger.info(f"[OK] System checks passed")
        logger.info(f"  - GPU: {env_status.gpu_name if env_status else 'N/A'}")
        logger.info(f"  - VRAM: {env_status.total_vram_gb if env_status else 0}GB")
        cuda_status = "Available" if env_status and env_status.cuda_available else "Unavailable"
        logger.info(f"  - CUDA: {cuda_status}")
        
        # 3. Initialize storage
        self.db = Database(str(self.config.db_path / "helm_decisions.db"))
        logger.info("[OK] Database initialized")
        
        # 4. Initialize validator
        self.validator = Validator(self.config)
        logger.info("[OK] Validator initialized")
        
        # 5. Initialize LLM (optional)
        self.local_model = None
        self.api_model = None
        
        # Demo mode forces safe defaults
        if self.config.DEMO_MODE:
            enable_local_model = False
            self.config.use_local_model = False

        if enable_local_model and self.config.use_local_model:
            try:
                model_config = ModelConfig(
                    model_id=self.config.default_model,
                    quantization=self.config.quantization
                )
                self.local_model = LocalModel(model_config)
                
                if self.local_model.load():
                    logger.info(f"[OK] Local model loaded: {self.config.default_model}")
                else:
                    logger.warning("Local model loading failed, will fallback to API")
                    self.local_model = None
            
            except Exception as e:
                logger.error(f"Failed to initialize local model: {e}")
                self.local_model = None
        
        # 6. Initialize API model (fallback)
        # If a local or api model was injected (for tests), use those
        if local_model is not None:
            self.local_model = local_model
        if api_model is not None:
            self.api_model = api_model

        if not self.local_model and not self.api_model:
            self.api_model = APIModel(
                api_endpoint=self.config.api_endpoint,
                api_key=self.config.api_key,
                model_name=self.config.api_model
            )
            try:
                self.api_model.load()
                logger.info(f"[OK] API model configured: {self.config.api_model}")
            except Exception as e:
                logger.warning(f"API model failed to load: {e}")
        
        # 7. Initialize agents
        self.head_agent = HeadAgent(self.config, self.validator)
        self.strategy_agent = StrategyAgent(self.config, self.local_model or self.api_model)
        self.finance_agent = FinanceAgent(self.config, self.local_model or self.api_model)
        
        # Register agents with head agent
        self.head_agent.register_agent(AgentType.STRATEGY, self.strategy_agent)
        self.head_agent.register_agent(AgentType.FINANCE, self.finance_agent)
        logger.info("[OK] All agents initialized and registered")
        
        # 8. Initialize dashboard (optional) - dynamic import to avoid Streamlit
        self.dashboard = None
        if enable_dashboard:
            try:
                from .ui.dashboard import Dashboard  # type: ignore
                self.dashboard = Dashboard(config=self.config)
                if self.dashboard.start():
                    logger.info(f"[OK] Dashboard ready at {self.config.dashboard_host}:{self.config.dashboard_port}")
                else:
                    logger.warning("Dashboard disabled (Streamlit not available)")
            except Exception as e:
                logger.warning(f"Dashboard component unavailable: {e}")
        
        logger.info("=" * 60)
        logger.info("HELM v2.0 - Initialization Complete")
        logger.info("=" * 60)
    
    def process_decision(self, prompt: str, context: dict, required_fields: list) -> dict:
        """Process a decision request through HELM
        
        Args:
            prompt: User prompt/request
            context: Decision context
            required_fields: Required fields for validation
            
        Returns:
            dict: Final decision
        """
        # Create decision input
        decision_input = DecisionInput(
            prompt=prompt,
            context=context,
            user_id=context.get('user_id', 'system'),
            session_id=context.get('session_id', 'default'),
            required_fields=required_fields
        )
        
        # Process through head agent
        decision = self.head_agent.process(decision_input)
        
        # Store decision
        self.db.insert_decision(decision)
        logger.info(f"Decision stored: {decision.decision_id}")
        
        return decision.to_dict()
    
    def get_decision_history(self, limit: int = 10) -> list:
        """Get recent decision history
        
        Args:
            limit: Number of decisions to retrieve
            
        Returns:
            list: Recent decisions
        """
        return self.db.get_recent_decisions(limit)
    
    def get_statistics(self) -> dict:
        """Get system statistics
        
        Returns:
            dict: Statistics
        """
        return self.db.get_statistics()
    
    def shutdown(self):
        """Shutdown HELM system"""
        logger.info("HELM v2.0 - Shutdown initiated")
        
        if self.local_model:
            self.local_model.unload()
            logger.info("[OK] Local model unloaded")
        
        if self.api_model:
            self.api_model.unload()
            logger.info("[OK] API model disconnected")
        
        if self.dashboard:
            self.dashboard.stop()
            logger.info("[OK] Dashboard stopped")
        
        self.db.disconnect()
        logger.info("[OK] Database connection closed")
        
        logger.info("HELM v2.0 - Shutdown complete")


def main():
    """Main application entry point"""
    try:
        # Initialize HELM
        helm = HELM(enable_local_model=True, enable_dashboard=False)
        
        # Example decision request
        prompt = "Should we proceed with this financial investment?"
        context = {
            'user_id': 'user_123',
            'session_id': 'session_001',
            'revenue': 100000,
            'costs': 60000,
            'investment': 50000,
            'expected_returns': 75000,
            'timeframe_years': 2,
            'objectives': ['Increase revenue', 'Expand market share'],
            'constraints': ['Limited budget', 'Timeline: 6 months'],
            'resources': ['Team of 5', 'Technology platform', 'Marketing budget']
        }
        required_fields = ['revenue', 'costs', 'investment', 'expected_returns']
        
        # Process decision
        logger.info(f"Processing: {prompt}")
        decision = helm.process_decision(prompt, context, required_fields)
        
        # Display result
        logger.info("=" * 60)
        logger.info("DECISION RESULT")
        logger.info("=" * 60)
        logger.info(f"Decision ID: {decision.get('decision_id')}")
        logger.info(f"Agent: {decision.get('agent_used')}")
        logger.info(f"Status: {decision.get('status')}")
        logger.info(f"Confidence: {decision.get('confidence'):.2%}")
        logger.info(f"Decision: {decision.get('decision_text')}")
        logger.info(f"ROI Estimate: {decision.get('roi_estimate'):.2%}")
        logger.info("=" * 60)
        
        # Show stats
        stats = helm.get_statistics()
        logger.info(f"Total Decisions: {stats.get('total_decisions', 0)}")
        logger.info(f"Acceptance Rate: {stats.get('accepted_decisions', 0) / max(stats.get('total_decisions', 1), 1):.1%}")
        
        # Shutdown
        helm.shutdown()
    
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
