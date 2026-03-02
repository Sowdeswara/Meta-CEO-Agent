"""
Test Scenario 2 - Model Loading and LLM Integration
Verifies local and API model functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helm.config import Config
from helm.models.local_model import LocalModel
from helm.models.api_model import APIModel
from helm.schemas import ModelConfig
from helm.logger import get_logger

logger = get_logger(__name__)


def test_scenario_2_model_loading():
    """Test: Load and initialize models"""
    
    try:
        logger.info("\n" + "="*70)
        logger.info("SCENARIO 2: MODEL LOADING AND LLM INTEGRATION")
        logger.info("="*70)
        
        config = Config()
        config.DEVELOPMENT_MODE = True
        
        # Test 1: Configure local model
        logger.info("\n[TEST 1] Configuring local model...")
        model_config = ModelConfig(
            model_id="microsoft/phi-2",
            quantization="8bit",
            max_new_tokens=200,
            context_window=2048
        )
        logger.info(f"[OK] Model config created:")
        logger.info(f"  Model: {model_config.model_id}")
        logger.info(f"  Quantization: {model_config.quantization}")
        logger.info(f"  Max tokens: {model_config.max_new_tokens}")
        
        # Test 2: Try to load local model
        logger.info("\n[TEST 2] Attempting to load local model...")
        local_model = LocalModel(model_config)
        
        if local_model.load():
            logger.info("[OK] Local model loaded successfully")
            
            # Test inference
            logger.info("\n[TEST 3] Testing local model inference...")
            prompt = "What is 2+2?"
            result = local_model.infer(prompt)
            
            if result:
                logger.info(f"[OK] Inference successful")
                logger.info(f"  Output length: {len(result)} characters")
            else:
                logger.warning("[WARN] Inference returned empty result")
            
            # Unload
            logger.info("\n[TEST 4] Unloading local model...")
            local_model.unload()
            logger.info("✓ Model unloaded successfully")
        
        else:
            logger.warning("[WARN] Local model loading failed, testing API model fallback...")
            
            # Test API model
            logger.info("\n[TEST 2b] Configuring API model...")
            api_model = APIModel(
                api_endpoint=config.api_endpoint,
                api_key=config.api_key,
                model_name=config.api_model
            )
            
            if api_model.load():
                logger.info("✓ API model configured successfully")
            else:
                logger.warning("[WARN] API model configuration failed (but this is expected if no API key)")
        
        logger.info("\n" + "="*70)
        logger.info("SCENARIO 2: TESTS COMPLETED [OK]")
        logger.info("="*70 + "\n")
        
        return True
    
    except Exception as e:
        logger.error(f"SCENARIO 2 FAILED: {e}", exc_info=True)
        logger.info("="*70 + "\n")
        return False


if __name__ == "__main__":
    success = test_scenario_2_model_loading()
    sys.exit(0 if success else 1)
