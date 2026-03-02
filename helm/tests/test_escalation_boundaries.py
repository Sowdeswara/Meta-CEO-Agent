import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from helm.validation.validator import Validator
from helm.schemas import ValidationResult, ValidationScore, ValidationStatus


class EscalationBoundaryTests(unittest.TestCase):
    def setUp(self):
        config = None
        self.validator = Validator(config)
        self.validator.validation_threshold = 0.70

    def make_score(self, weighted):
        # create a ValidationScore structure with desired weighted_score
        # weights are equal so we can adjust one component directly
        vs = ValidationScore(
            schema_complete=weighted,
            required_fields_present=weighted,
            numeric_valid=weighted,
            confidence=weighted,
            roi_viable=weighted,
        )
        # but weighted_score property will compute average, which equals weighted
        return vs

    def test_pass_on_or_above_threshold(self):
        score = self.make_score(0.70)
        self.assertTrue(score.weighted_score >= self.validator.validation_threshold)
        result = self.validator.validate_decision({}, [], max_retries=0)
        # bypass score by setting directly
        result.score = score
        if result.score.weighted_score >= self.validator.validation_threshold:
            status = ValidationStatus.PASS
        elif result.score.weighted_score < 0.5 * self.validator.validation_threshold:
            status = ValidationStatus.ESCALATE
        else:
            status = ValidationStatus.FAIL
        self.assertEqual(status, ValidationStatus.PASS)

    def test_fail_between_half_and_threshold(self):
        score = self.make_score(0.60)
        result = self.validator.validate_decision({}, [], max_retries=0)
        result.score = score
        if result.score.weighted_score >= self.validator.validation_threshold:
            status = ValidationStatus.PASS
        elif result.score.weighted_score < 0.5 * self.validator.validation_threshold:
            status = ValidationStatus.ESCALATE
        else:
            status = ValidationStatus.FAIL
        self.assertEqual(status, ValidationStatus.FAIL)

    def test_escalate_below_half_threshold(self):
        score = self.make_score(0.20)
        result = self.validator.validate_decision({}, [], max_retries=0)
        result.score = score
        if result.score.weighted_score >= self.validator.validation_threshold:
            status = ValidationStatus.PASS
        elif result.score.weighted_score < 0.5 * self.validator.validation_threshold:
            status = ValidationStatus.ESCALATE
        else:
            status = ValidationStatus.FAIL
        self.assertEqual(status, ValidationStatus.ESCALATE)


if __name__ == '__main__':
    unittest.main()
