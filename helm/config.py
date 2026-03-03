"""
Configuration management for HELM v2.0
Central configuration for deterministic system
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Central configuration management for HELM v2.0"""
    
    def __init__(self):
        # ============== PATHS ==============
        self.root_path = Path(__file__).parent.parent  # Agent/
        self.helm_path = Path(__file__).parent  # Agent/helm/
        self.model_cache = self.root_path / "models_cache"
        self.db_path = self.helm_path / "storage"
        self.logs_path = self.root_path / "logs"
        
        # ============== ENVIRONMENT ==============
        # GPU/CUDA settings
        self.use_gpu = os.getenv("USE_GPU", "True").lower() == "true"
        self.use_local_model = os.getenv("USE_LOCAL_MODEL", "True").lower() == "true"
        self.gpu_memory_fraction = float(os.getenv("GPU_MEMORY_FRACTION", "0.9"))
        self.device_map = os.getenv("DEVICE_MAP", "auto")
        
        # ============== MODEL CONFIGURATION ==============
        # Local model settings
        self.default_model = os.getenv("DEFAULT_MODEL", "microsoft/phi-2")
        self.quantization = os.getenv("QUANTIZATION", "8bit")  # 4bit, 8bit, 16bit
        self.max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "200"))
        self.context_window = int(os.getenv("CONTEXT_WINDOW", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.3"))
        
        # API model settings
        self.api_endpoint = os.getenv("API_ENDPOINT", "https://api.openai.com/v1/chat/completions")
        self.api_key = os.getenv("API_KEY", "")
        self.api_model = os.getenv("API_MODEL", "gpt-3.5-turbo")
        
        # ============== VALIDATION THRESHOLDS ==============
        self.validation_threshold = float(os.getenv("VALIDATION_THRESHOLD", "0.70"))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
        self.roi_threshold = float(os.getenv("ROI_THRESHOLD", "0.0"))
        
        # ============== RETRY LOGIC ==============
        self.max_retries = int(os.getenv("MAX_RETRIES", "2"))
        self.retry_backoff = float(os.getenv("RETRY_BACKOFF", "1.0"))
        
        # ============== ARBITRATION SETTINGS ==============
        # weights for strategy vs finance components (must sum 1.0)
        self.ARBITRATION_WEIGHTS = {
            "strategy": float(os.getenv("ARBITRATION_WEIGHT_STRATEGY", "0.5")),
            "finance": float(os.getenv("ARBITRATION_WEIGHT_FINANCE", "0.5"))
        }
        self.RISK_PENALTY_FACTOR = float(os.getenv("RISK_PENALTY_FACTOR", "0.5"))
        
        # ============== SYSTEM SETTINGS ==============
        self.debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.enable_dashboard = os.getenv("ENABLE_DASHBOARD", "True").lower() == "true"
        self.dashboard_host = os.getenv("DASHBOARD_HOST", "localhost")
        self.dashboard_port = int(os.getenv("DASHBOARD_PORT", "8501"))
        
        # ============== CURRENCY ==============
        self.default_currency = os.getenv("DEFAULT_CURRENCY", "USD")
        # ======= DEVELOPMENT / DEMO FLAGS ========
        # When True, allows skipping environment checks for tests and local development
        self.DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False").lower() == "true"
        # When True, disable GPU and use safe demo stubs
        self.DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() == "true"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for path in [self.model_cache, self.db_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return getattr(self, key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            'root_path': str(self.root_path),
            'helm_path': str(self.helm_path),
            'use_gpu': self.use_gpu,
            'use_local_model': self.use_local_model,
            'default_model': self.default_model,
            'quantization': self.quantization,
            'validation_threshold': self.validation_threshold,
            'max_retries': self.max_retries,
            'debug_mode': self.debug_mode,
            'DEVELOPMENT_MODE': self.DEVELOPMENT_MODE,
            'DEMO_MODE': self.DEMO_MODE,
            'arbitration_weights': self.ARBITRATION_WEIGHTS,
            'risk_penalty_factor': self.RISK_PENALTY_FACTOR
        }
DEMO_MODE = True
USE_LOCAL_MODEL = False
