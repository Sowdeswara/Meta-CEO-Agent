"""
Local Model - Load and run models locally on GPU/CPU
VRAM-aware implementation for RTX 3050 (6GB)
"""

import logging
from typing import Any, Dict, Optional

from .interface import ModelInterface
from ..schemas import ModelConfig


logger = logging.getLogger(__name__)


class LocalModel(ModelInterface):
    """Local model implementation supporting GPU inference with VRAM management"""
    
    def __init__(self, config: ModelConfig = None):
        """Initialize LocalModel"""
        self.config = config or ModelConfig()
        self.model = None
        self.tokenizer = None
        self.device = None
        self.loaded = False
    
    def load(self) -> bool:
        """Load model and tokenizer with VRAM handling"""
        try:
            logger.info(f"Loading model: {self.config.model_id}")
            logger.info(f"Quantization: {self.config.quantization}")
            
            # Import torch here to handle potential CUDA errors
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Check CUDA availability
            if not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                self.device = "cpu"
            else:
                # Check available VRAM
                total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                available_vram = (torch.cuda.get_device_properties(0).total_memory - 
                                 torch.cuda.memory_allocated(0)) / (1024**3)
                
                logger.info(f"Total VRAM: {total_vram:.2f}GB, Available: {available_vram:.2f}GB")
                
                if available_vram < 0.5:
                    logger.error(f"Insufficient VRAM: {available_vram:.2f}GB available")
                    return False
                
                self.device = "cuda"
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_id)
            
            # Load model with appropriate quantization
            logger.info(f"Loading model with {self.config.quantization} quantization...")
            
            if self.config.quantization == "8bit" and self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_id,
                    load_in_8bit=True,
                    device_map="auto",
                    torch_dtype="auto"
                )
            elif self.config.quantization == "4bit" and self.device == "cuda":
                try:
                    from transformers import BitsAndBytesConfig
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True
                    )
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.config.model_id,
                        quantization_config=bnb_config,
                        device_map="auto"
                    )
                except ImportError:
                    logger.warning("bitsandbytes not available, using 8bit")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.config.model_id,
                        load_in_8bit=True,
                        device_map="auto"
                    )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
            
            self.model.eval()
            self.loaded = True
            
            # Log memory usage
            if self.device == "cuda":
                vram_used = torch.cuda.memory_allocated(0) / (1024**3)
                logger.info(f"Model loaded. VRAM used: {vram_used:.2f}GB")
            
            logger.info("Model loaded successfully")
            return True
        
        except Exception as e:
            # Handle explicit CUDA OOM if torch available
            try:
                import torch
                if isinstance(e, getattr(torch.cuda, 'OutOfMemoryError', type(e))):
                    logger.warning(f"CUDA OOM during model load: {e}")
                else:
                    logger.error(f"Failed to load model: {e}")
            except Exception:
                logger.error(f"Failed to load model: {e}")

            self.loaded = False
            return False
    
    def unload(self) -> bool:
        """Unload model from memory"""
        try:
            if self.model is not None:
                del self.model
            if self.tokenizer is not None:
                del self.tokenizer
            
            # Clear CUDA cache
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except:
                pass
            
            self.model = None
            self.tokenizer = None
            self.loaded = False
            logger.info("Model unloaded successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to unload model: {e}")
            return False
    
    def infer(self, input_text: str, max_tokens: Optional[int] = None) -> str:
        """Run local inference"""
        if not self.loaded:
            logger.error("Model not loaded")
            return ""
        
        try:
            import torch
            
            max_tokens = max_tokens or self.config.max_new_tokens
            
            # Tokenize input
            inputs = self.tokenizer(input_text, return_tensors="pt")
            
            # Move to device
            if self.device == "cuda":
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    use_cache=self.config.use_cache
                )
            
            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.debug(f"Inference completed. Output length: {len(response)}")
            return response
        
        except Exception as e:
            try:
                import torch
                if isinstance(e, getattr(torch.cuda, 'OutOfMemoryError', type(e))):
                    logger.warning(f"CUDA OOM during inference: {e}")
                else:
                    logger.error(f"Inference failed: {e}")
            except Exception:
                logger.error(f"Inference failed: {e}")
            return ""
    
    def get_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            'model_id': self.config.model_id,
            'quantization': self.config.quantization,
            'max_new_tokens': self.config.max_new_tokens,
            'context_window': self.config.context_window,
            'device': self.device,
            'loaded': self.loaded
        }
