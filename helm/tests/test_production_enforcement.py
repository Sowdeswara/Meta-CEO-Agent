import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.main import HELM
from helm.config import Config
from helm.errors import MissingDependencyError

class ProductionEnforcementTests(unittest.TestCase):
    def test_skip_system_check_only_in_dev(self):
        cfg = Config()
        cfg.DEVELOPMENT_MODE = False
        # production should not allow skipping
        with self.assertRaises(RuntimeError):
            HELM(skip_system_check=True, config=cfg)

        cfg.DEVELOPMENT_MODE = True
        # now skip must be allowed
        helm = HELM(skip_system_check=True, config=cfg)
        helm.shutdown()

    def test_missing_dependency_error_raised(self):
        cfg = Config()
        cfg.DEVELOPMENT_MODE = False
        # simulate missing by forcing environment check raise
        # we can't easily modify system_check behavior, but we can call HELM and expect error if dependencies absent
        # since tests run without torch/requests, HELM initialization should raise MissingDependencyError
        with self.assertRaises(Exception) as cm:
            HELM(config=cfg)
        self.assertTrue(isinstance(cm.exception, RuntimeError) or isinstance(cm.exception, MissingDependencyError))

if __name__ == '__main__':
    unittest.main()
