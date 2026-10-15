"""UKG Ready deduction validation; mapping is connected."""
import copy
import unittest
from normalization.adapters import ukg_ready
from pydantic import ValidationError
from normalization.source_models.ukg_ready.ukg_ready_source_model_deduction import UKGReadyDeductionInput


class UKGReadyDeductionValidationChecks(unittest.TestCase):
    def assert_valid(self, entity, payload):
        before = copy.deepcopy(payload)
        result = ukg_ready.normalize(entity, payload, {}, employee_id="007")
        self.assertIsInstance(result["deductions"], list)
        self.assertEqual(payload, before)

    def test_deduction_all_sections_and_native_wrappers(self):
        self.assert_valid("deduction", {"assignments": {"deductions": [{"id": 1}]},
                                       "code_lookup": {"items": [{"id": None}]},
                                       "benefits": {"benefits": [{"id": 2, "benefit_plan": {"id": 3}}]}})
        self.assert_valid("deduction", {"deductions": [{"id": 1}], "items": [{"id": 2}],
                                       "benefits": [{"id": 3}]})
        for payload in [{}, {"assignments": None}, {"deductions": []},
                        {"items": []}, {"benefits": []}]:
            self.assertEqual(ukg_ready.normalize("deduction", payload, {}, employee_id="007")["deductions"], [])
        for payload in [{"assignments": {}}, {"code_lookup": {}},
                        {"benefits": {"benefits": [{"id": 1, "benefit_plan": {}}]}},
                        {"deductions": [{"id": 1, "sequence": []}]},
                        {"assignments": {"deductions": [{"id": 1}]}, "code_lookup": {"items": [{}]}}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                ukg_ready.normalize("deduction", payload, {}, employee_id="007")

    def test_deduction_sections_and_native_responses(self):
        payload = {"assignments": {"deductions": [{"id": 1}]},
                   "code_lookup": {"items": [{"id": None, "code": "source"}]},
                   "benefits": {"benefits": [{"id": 2, "benefit_plan": {"id": 3}}]}}
        before = copy.deepcopy(payload)
        UKGReadyDeductionInput.validate_response(payload)
        UKGReadyDeductionInput.validate_response({"deductions": [{"id": 1}],
                                                  "items": [{"id": None}], "benefits": [{"id": 2}]})
        self.assertEqual(payload, before)
        for bad in [{"assignments": {}}, {"code_lookup": {}},
                    {"benefits": {"benefits": [{"id": 2, "benefit_plan": {}}]}}]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                UKGReadyDeductionInput.validate_response(bad)

    def test_optional_supplements_and_conflicting_representations(self):
        UKGReadyDeductionInput.validate_response({"assignments": None, "code_lookup": None, "benefits": None})
        payload = {"assignments": {}, "deductions": []}
        with self.subTest(payload=payload), self.assertRaises(ValueError):
            UKGReadyDeductionInput.validate_response(payload)

