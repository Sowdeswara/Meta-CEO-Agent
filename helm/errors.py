"""
HELM custom exceptions
"""

from typing import List


class MissingDependencyError(Exception):
    """Raised when critical dependencies are missing for production run."""

    def __init__(self, missing: List[str]):
        self.missing = missing
        super().__init__(f"Missing critical dependencies: {', '.join(missing)}")


class GPUFailureError(Exception):
    """Raised when GPU model load or inference fails irrecoverably."""

    def __init__(self, message: str):
        super().__init__(message)
