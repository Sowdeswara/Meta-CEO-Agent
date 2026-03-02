"""
Model Interface - Abstract base for all models
Defines contract for both local and API models
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ModelInterface(ABC):
    """Abstract interface for model implementations"""
    
    @abstractmethod
    def load(self) -> bool:
        """Load the model
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def unload(self) -> bool:
        """Unload the model from memory
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def infer(self, input_data: str) -> str:
        """Run inference on input data
        
        Args:
            input_data: Input text/prompt
            
        Returns:
            str: Model output text
        """
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get model configuration
        
        Returns:
            Dict with model configuration and status
        """
        pass
