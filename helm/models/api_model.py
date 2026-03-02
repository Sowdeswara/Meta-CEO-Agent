"""
API Model - Call external model APIs with fallback support
"""

import logging
from typing import Any, Dict, Optional

from .interface import ModelInterface


logger = logging.getLogger(__name__)


class APIModel(ModelInterface):
    """API-based model implementation with fallback support"""
    
    def __init__(self, api_endpoint: str, api_key: str = "", model_name: str = "gpt-3.5-turbo"):
        """Initialize APIModel
        
        Args:
            api_endpoint: API endpoint URL
            api_key: API authentication key
            model_name: Model identifier at the API
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model_name = model_name
        self.session = None
        self.loaded = False
    
    def load(self) -> bool:
        """Initialize API connection"""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}' if self.api_key else '',
                'Content-Type': 'application/json'
            })
            self.loaded = True
            logger.info(f"API connection initialized: {self.api_endpoint}")
            return True
        
        except ImportError as e:
            logger.error(f"requests library not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize API connection: {e}")
            return False
    
    def unload(self) -> bool:
        """Close API connection"""
        try:
            if self.session:
                self.session.close()
            self.loaded = False
            logger.info("API connection closed")
            return True
        except Exception as e:
            logger.error(f"Error closing API connection: {e}")
            return False
    
    def infer(self, input_text: str, max_tokens: int = 200) -> str:
        """Call API for inference
        
        Args:
            input_text: Input prompt
            max_tokens: Maximum response tokens
            
        Returns:
            str: API response text
        """
        if not self.loaded:
            logger.error("API not loaded")
            return ""
        
        try:
            import requests
            
            # Prepare request payload
            payload = {
                'model': self.model_name,
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful decision support assistant. Provide concise, structured responses.'},
                    {'role': 'user', 'content': input_text}
                ],
                'max_tokens': max_tokens,
                'temperature': 0.3
            }
            
            logger.debug(f"Sending request to {self.api_endpoint}")
            
            # Make request with timeout
            response = self.session.post(
                self.api_endpoint,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract text based on API format
            if 'choices' in result and len(result['choices']) > 0:
                text = result['choices'][0].get('message', {}).get('content', '')
            elif 'text' in result:
                text = result['text']
            else:
                text = str(result)
            
            logger.debug(f"API response received: {len(text)} characters")
            return text
        
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            return ""
        except requests.exceptions.ConnectionError:
            logger.error("API connection error")
            return ""
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e}")
            return ""
        except Exception as e:
            logger.error(f"API inference failed: {e}")
            return ""
    
    def get_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return {
            'api_endpoint': self.api_endpoint,
            'model_name': self.model_name,
            'loaded': self.loaded,
            'type': 'api'
        }
