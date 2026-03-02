"""
HELM v2.0 - Data Schemas and Models
Pydantic schemas for deterministic validation and typing
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from enum import Enum


class AgentType(str, Enum):
    """Agent type enumeration"""
    HEAD = "head"
    STRATEGY = "strategy"
    FINANCE = "finance"
    ESCALATION = "escalation"


class ValidationStatus(str, Enum):
    """Validation status enumeration"""
    PASS = "pass"
    FAIL = "fail"
    RETRY = "retry"
    ESCALATE = "escalate"


class DecisionStatus(str, Enum):
    """Decision status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ESCALATED = "escalated"


@dataclass
class DecisionInput:
    """Input structure for decision processing"""
    prompt: str
    context: Dict[str, Any]
    user_id: str
    session_id: str
    required_fields: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ValidationScore:
    """Deterministic validation scoring"""
    schema_complete: float  # 0-1
    required_fields_present: float  # 0-1
    numeric_valid: float  # 0-1
    confidence: float  # 0-1
    roi_viable: float  # 0-1
    
    @property
    def weighted_score(self) -> float:
        """Calculate weighted validation score"""
        weights = {
            'schema_complete': 0.20,
            'required_fields': 0.20,
            'numeric_valid': 0.20,
            'confidence': 0.20,
            'roi_viable': 0.20
        }
        return (
            self.schema_complete * weights['schema_complete'] +
            self.required_fields_present * weights['required_fields'] +
            self.numeric_valid * weights['numeric_valid'] +
            self.confidence * weights['confidence'] +
            self.roi_viable * weights['roi_viable']
        )
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'schema_complete': self.schema_complete,
            'required_fields_present': self.required_fields_present,
            'numeric_valid': self.numeric_valid,
            'confidence': self.confidence,
            'roi_viable': self.roi_viable,
            'weighted_score': self.weighted_score
        }


@dataclass
class ValidationResult:
    """Result of validation process"""
    status: ValidationStatus
    score: ValidationScore
    errors: List[str]
    warnings: List[str]
    retry_count: int = 0
    
    def passed(self, threshold: float = 0.70) -> bool:
        """Check if validation passed threshold"""
        return self.score.weighted_score >= threshold
    
    def can_retry(self, max_retries: int = 2) -> bool:
        """Check if retry is possible"""
        return self.retry_count < max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'score': self.score.to_dict(),
            'errors': self.errors,
            'warnings': self.warnings,
            'retry_count': self.retry_count
        }


@dataclass
class StructuredDecision:
    """Final structured decision object"""
    decision_id: str
    agent_used: AgentType
    decision_text: str
    confidence: float  # 0-1
    risk_level: str  # "low", "medium", "high"
    roi_estimate: float  # percentage
    reasoning: Dict[str, Any]
    validation_score: float
    status: DecisionStatus
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['agent_used'] = self.agent_used.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ModelConfig:
    """Model configuration parameters"""
    model_id: str
    quantization: Literal["4bit", "8bit", "16bit", "none"] = "8bit"
    max_new_tokens: int = 200
    context_window: int = 2048
    temperature: float = 0.3
    top_p: float = 0.95
    device_map: str = "auto"
    use_cache: bool = True


@dataclass
class EnvironmentStatus:
    """Current environment status"""
    cuda_available: bool
    gpu_count: int
    gpu_name: str
    total_vram_gb: float
    available_vram_gb: float
    python_version: str
    torch_version: str
    transformers_version: str
    pydantic_installed: bool
    requests_installed: bool
    streamlit_installed: bool
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
