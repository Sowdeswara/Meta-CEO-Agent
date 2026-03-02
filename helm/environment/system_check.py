"""
System Environment Checks - Verify GPU, CUDA, and dependencies
Production-grade environment validation
"""

from typing import Tuple
import logging
import sys

from ..schemas import EnvironmentStatus


logger = logging.getLogger(__name__)


class SystemCheck:
    """System environment validation with comprehensive checks"""
    
    def __init__(self):
        """Initialize SystemCheck"""
        self.required_packages = {
            'torch': '2.0.0',
            'transformers': '4.30.0',
            'pydantic': '2.0.0',
            'requests': '2.31.0'
        }
        self.optional_packages = {
            'streamlit': '1.28.0',
            'pyyaml': '6.0'
        }
    
    def check_environment(self, raise_on_missing: bool = False) -> Tuple[bool, EnvironmentStatus]:
        """Check complete environment and return status

        If raise_on_missing is True, raise MissingDependencyError when critical packages are missing.
        """
        try:
            status = EnvironmentStatus(
                cuda_available=self.check_cuda(),
                gpu_count=self.get_gpu_count(),
                gpu_name=self.get_gpu_name(),
                total_vram_gb=self.get_total_vram(),
                available_vram_gb=self.get_available_vram(),
                python_version=self.get_python_version(),
                torch_version=self.get_torch_version(),
                transformers_version=self.get_transformers_version(),
                pydantic_installed=self.check_package('pydantic'),
                requests_installed=self.check_package('requests'),
                streamlit_installed=self.check_package('streamlit')
            )
            
            checks = {
                'python': self.check_python_version(),
                'torch': self.check_torch(),
                'transformers': self.check_transformers(),
                'pydantic': self.check_pydantic(),
                'requests': self.check_requests()
            }
            all_critical_passed = all(checks.values())
            missing = [k for k, v in checks.items() if not v]
            
            logger.info(f"Environment Check: {'PASSED' if all_critical_passed else 'FAILED'}")
            logger.debug(f"Environment Status: {status.to_dict()}")

            if raise_on_missing and missing:
                try:
                    from ..errors import MissingDependencyError
                except Exception:
                    # Fallback to generic Exception if import fails
                    raise Exception(f"Missing critical dependencies: {', '.join(missing)}")
                raise MissingDependencyError(missing)

            return all_critical_passed, status
        
        except Exception as e:
            logger.error(f"Environment check failed: {e}")
            return False, None
    
    def check_python_version(self) -> bool:
        """Check Python version >= 3.10"""
        version = sys.version_info
        passed = version.major >= 3 and version.minor >= 10
        logger.info(f"Python {version.major}.{version.minor}: {'[OK]' if passed else '[ERROR]'}")
        return passed
    
    def get_python_version(self) -> str:
        """Get Python version string"""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def check_cuda(self) -> bool:
        """Check CUDA availability"""
        try:
            import torch
            available = torch.cuda.is_available()
            logger.info(f"CUDA Available: {'[OK]' if available else '[ERROR]'}")
            return available
        except ImportError:
            logger.error("PyTorch not installed")
            return False
    
    def get_gpu_count(self) -> int:
        """Get number of GPUs"""
        try:
            import torch
            count = torch.cuda.device_count()
            logger.info(f"GPU Count: {count}")
            return count
        except:
            return 0
    
    def get_gpu_name(self) -> str:
        """Get GPU device name"""
        try:
            import torch
            if torch.cuda.is_available():
                name = torch.cuda.get_device_name(0)
                logger.info(f"GPU Device: {name}")
                return name
            return "No GPU"
        except:
            return "Unknown"
    
    def get_total_vram(self) -> float:
        """Get total VRAM in GB"""
        try:
            import torch
            if torch.cuda.is_available():
                total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"Total VRAM: {total:.2f} GB")
                return round(total, 2)
            return 0.0
        except:
            return 0.0
    
    def get_available_vram(self) -> float:
        """Get available VRAM in GB"""
        try:
            import torch
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated(0) / (1024**3)
                reserved = torch.cuda.memory_reserved(0) / (1024**3)
                total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                available = total - allocated
                logger.info(f"Available VRAM: {available:.2f} GB (Allocated: {allocated:.2f})")
                return round(available, 2)
            return 0.0
        except:
            return 0.0
    
    def get_torch_version(self) -> str:
        """Get PyTorch version"""
        try:
            import torch
            return torch.__version__
        except:
            return "Not installed"
    
    def get_transformers_version(self) -> str:
        """Get Transformers version"""
        try:
            import transformers
            return transformers.__version__
        except:
            return "Not installed"
    
    def check_torch(self) -> bool:
        """Check PyTorch is installed"""
        return self.check_package('torch')
    
    def check_transformers(self) -> bool:
        """Check Transformers is installed"""
        return self.check_package('transformers')
    
    def check_pydantic(self) -> bool:
        """Check Pydantic is installed"""
        return self.check_package('pydantic')
    
    def check_requests(self) -> bool:
        """Check Requests is installed"""
        return self.check_package('requests')
    
    def check_package(self, package_name: str) -> bool:
        """Check if package is installed"""
        try:
            __import__(package_name)
            logger.debug(f"Package '{package_name}': [OK]")
            return True
        except ImportError:
            logger.warning(f"Package '{package_name}': [ERROR]")
            return False
    
    def check_dependencies(self) -> bool:
        """Check all critical dependencies"""
        checks = {
            'torch': self.check_torch(),
            'transformers': self.check_transformers(),
            'pydantic': self.check_pydantic(),
            'requests': self.check_requests()
        }
        all_passed = all(checks.values())
        logger.info(f"Dependencies Check: {'PASSED' if all_passed else 'FAILED'}")
        return all_passed
    
    def check_vram_sufficient(self, required_gb: float = 1.0) -> bool:
        """Check if sufficient VRAM is available"""
        available = self.get_available_vram()
        sufficient = available >= required_gb
        logger.info(f"VRAM Sufficient ({required_gb}GB): {'[OK]' if sufficient else '[ERROR]'}")
        return sufficient
