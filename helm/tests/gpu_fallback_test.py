"""
GPU Fallback Test - simulate LocalModel CUDA failure and verify API fallback
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helm import HELM
from helm.config import Config
from helm.models.api_model import APIModel
from helm.schemas import ModelConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FakeOOMLocalModel:
    """Simulate a local model that fails due to CUDA OOM"""
    def __init__(self, *args, **kwargs):
        self.loaded = False

    def load(self):
        # Simulate CUDA OOM by returning False
        logger.warning("FakeOOMLocalModel: simulating CUDA OOM during load")
        return False

    def unload(self):
        return True

    def infer(self, *args, **kwargs):
        return ""

    def get_config(self):
        return {'model_id': 'fake', 'loaded': False}


def test_gpu_fallback():
    config = Config()
    config.DEVELOPMENT_MODE = True

    fake_local = FakeOOMLocalModel()
    # Provide a simple APIModel that may fail to load but should be set on HELM
    api = APIModel(api_endpoint=config.api_endpoint, api_key=config.api_key, model_name=config.api_model)

    helm = HELM(enable_local_model=True, enable_dashboard=False, skip_system_check=True, config=config, local_model=fake_local, api_model=api)

    # After initialization, local model should be absent (load failed) and api_model object present
    local_loaded = getattr(helm.local_model, 'loaded', False) if helm.local_model else False
    api_loaded = getattr(helm.api_model, 'loaded', False) if helm.api_model else False

    logger.info(f"Local loaded: {local_loaded}, API loaded: {api_loaded}")
    print({'local_loaded': local_loaded, 'api_loaded': api_loaded})
    return local_loaded, api_loaded


if __name__ == '__main__':
    test_gpu_fallback()
