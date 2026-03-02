"""
Validation and verification logic
Deterministic rule-based validation with weighted scoring
"""

import logging
from typing import Tuple, Dict, Any, List

from ..schemas import ValidationScore, ValidationResult, ValidationStatus, DecisionInput


logger = logging.getLogger(__name__)


class Validator:
    """Central validation service - Deterministic rule-based validation"""
    
    def __init__(self, config=None):
        """Initialize Validator"""
        self.config = config
        self.validation_threshold = config.validation_threshold if config else 0.70
        self.confidence_threshold = config.confidence_threshold if config else 0.65
        self.roi_threshold = config.roi_threshold if config else 0.0
    
    def validate_input(self, data: DecisionInput, required_fields: List[str]) -> Tuple[bool, str]:
        """Validate input data"""
        try:
            # Check required fields
            context = data.context if isinstance(data, DecisionInput) else data
            
            missing = []
            for field in required_fields:
                if field not in context or context[field] is None:
                    missing.append(field)
            
            if missing:
                return False, f"Missing required fields: {', '.join(missing)}"
            
            logger.info(f"Input validation passed for {len(required_fields)} fields")
            return True, "Valid"
        
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return False, str(e)
    
    def validate_output(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate output data"""
        try:
            # StructuredDecision uses 'decision_text' as the decision field
            required_output_fields = ['decision_text', 'confidence', 'reasoning']
            
            missing = [f for f in required_output_fields if f not in data]
            if missing:
                return False, f"Missing output fields: {', '.join(missing)}"
            
            # Check confidence is numeric and valid
            try:
                confidence = float(data.get('confidence', 0))
                if not (0 <= confidence <= 1):
                    return False, "Confidence must be between 0 and 1"
            except (ValueError, TypeError):
                return False, "Confidence must be numeric"
            
            logger.info("Output validation passed")
            return True, "Valid"
        
        except Exception as e:
            logger.error(f"Output validation error: {e}")
            return False, str(e)
    
    def validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data against schema"""
        try:
            required_fields = schema.get('required', [])
            field_types = schema.get('properties', {})
            
            # Check required fields
            missing = [f for f in required_fields if f not in data]
            if missing:
                return False, f"Missing required fields: {', '.join(missing)}"
            
            # Check field types
            type_errors = []
            for field, expected_type in field_types.items():
                if field in data:
                    actual_type = type(data[field]).__name__
                    if expected_type != actual_type:
                        type_errors.append(f"{field}: expected {expected_type}, got {actual_type}")
            
            if type_errors:
                return False, "; ".join(type_errors)
            
            logger.info("Schema validation passed")
            return True, "Valid"
        
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False, str(e)
    
    def calculate_validation_score(
        self,
        decision_data: Dict[str, Any],
        required_fields: List[str]
    ) -> ValidationScore:
        """Calculate deterministic weighted validation score"""
        
        # 1. Schema completeness (0-1)
        total_fields_possible = len(required_fields) + 5  # arbitrary additional fields
        present_fields = len([f for f in decision_data if f in required_fields])
        schema_complete = min(present_fields / len(required_fields), 1.0) if required_fields else 0.0
        
        # 2. Required fields present (0-1)
        missing_critical = sum(1 for f in required_fields if f not in decision_data or decision_data[f] is None)
        required_complete = max(1.0 - (missing_critical / len(required_fields)), 0.0) if required_fields else 0.0
        
        # 3. Numeric validity (0-1)
        numeric_valid = 1.0
        numeric_fields = {'confidence', 'roi', 'risk_score', 'impact', 'arbitration_score'}
        for field in numeric_fields:
            if field in decision_data:
                try:
                    val = float(decision_data[field])
                    # Confidence and ROI should be 0-1 or similar reasonable range
                    if field in {'confidence', 'roi'} and not (0 <= val <= 1.5):
                        numeric_valid = 0.8
                except (ValueError, TypeError):
                    numeric_valid = 0.0
                    break
        
        # 4. Confidence score (0-1)
        confidence = decision_data.get('confidence', 0)
        try:
            confidence = float(confidence)
            confidence = min(max(confidence, 0.0), 1.0)
        except (ValueError, TypeError):
            confidence = 0.0
        
        # 5. ROI viability (0-1)
        roi_viable = 1.0
        roi = decision_data.get('roi', self.roi_threshold)
        try:
            roi = float(roi)
            roi_viable = 1.0 if roi >= self.roi_threshold else 0.5
        except (ValueError, TypeError):
            roi_viable = 0.5
        
        score = ValidationScore(
            schema_complete=round(schema_complete, 2),
            required_fields_present=round(required_complete, 2),
            numeric_valid=round(numeric_valid, 2),
            confidence=round(confidence, 2),
            roi_viable=round(roi_viable, 2)
        )
        
        logger.debug(f"Validation Score: {score.to_dict()}")
        return score
    
    def validate_decision(
        self,
        decision_data: Dict[str, Any],
        required_fields: List[str],
        max_retries: int = 2
    ) -> ValidationResult:
        """Complete decision validation with retry logic"""
        
        logger.info(f"Starting validation with max_retries={max_retries}")
        
        # Calculate score
        score = self.calculate_validation_score(decision_data, required_fields)
        
        # Collect errors and warnings
        errors = []
        warnings = []
        
        # Validate input structure
        missing = [f for f in required_fields if f not in decision_data or decision_data[f] is None]
        if missing:
            errors.append(f"Missing fields: {', '.join(missing)}")
        
        # Validate numeric fields
        confidence = decision_data.get('confidence', 0)
        try:
            confidence = float(confidence)
            if confidence < self.confidence_threshold:
                warnings.append(f"Confidence {confidence} below threshold {self.confidence_threshold}")
        except (ValueError, TypeError):
            errors.append(f"Invalid confidence value: {confidence}")
        
        # Determine status and escalation logic
        if score.weighted_score >= self.validation_threshold:
            status = ValidationStatus.PASS
            logger.info(f"Validation PASSED (score: {score.weighted_score:.2f})")
        else:
            # If score is extremely low (much below threshold), escalate
            if score.weighted_score < (self.validation_threshold * 0.5):
                status = ValidationStatus.ESCALATE
                logger.warning(f"Validation ESCALATED (score: {score.weighted_score:.2f})")
            else:
                status = ValidationStatus.FAIL
                logger.warning(f"Validation FAILED (score: {score.weighted_score:.2f})")
        
        return ValidationResult(
            status=status,
            score=score,
            errors=errors,
            warnings=warnings,
            retry_count=0
        )
    
    def assess_risk(self, decision_data: Dict[str, Any]) -> str:
        """Assess risk level of decision"""
        risk_factors = 0
        
        confidence = decision_data.get('confidence', 0.5)
        try:
            confidence = float(confidence)
            if confidence < 0.5:
                risk_factors += 1
        except:
            risk_factors += 1
        
        roi = decision_data.get('roi', 0)
        try:
            roi = float(roi)
            if roi < 0:
                risk_factors += 2
        except:
            risk_factors += 1
        
        if risk_factors >= 2:
            return "high"
        elif risk_factors == 1:
            return "medium"
        else:
            return "low"
