"""UKG Ready employee validation; mapping is pending."""
import copy
import unittest
from normalization.adapters import ukg_ready
from pydantic import ValidationError
from normalization.source_models.ukg_ready.ukg_ready_source_model_employee import UKGReadyEmployeeInput


class UKGReadyEmployeeValidationChecks(unittest.TestCase):
    def assert_valid(self, entity, payload):
        before = copy.deepcopy(payload)
        self.assertIsInstance(ukg_ready.normalize(entity, payload, {}), list)
        self.assertEqual(payload, before)

    def test_employee_supplements_and_required_ids(self):
        self.assert_valid("employee", {"id": 1, "pay_info": {"pay_type": {"id": 2}},
                                      "compensation_history": {"compensations": [{"id": None, "amount": 0.0}]}})
        self.assert_valid("employee", {"employees": [{"id": 1, "pay_info": {"standard_work_day": 0}}]})
        self.assert_valid("employee", {"id": None, "pay_info": None})
        self.assertEqual(ukg_ready.normalize("employee", {"employees": []}, {}), [])
        for payload in [{}, {"id": 1, "pay_info": {"pay_type": {}}},
                        {"id": 1, "compensation_history": {}},
                        {"employees": [{"id": 1, "compensation_history": {"compensations": [{}]}}]}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                ukg_ready.normalize("employee", payload, {})

    def test_employee_and_supplements(self):
        payload = {"id": 1, "first_name": "Synthetic", "pay_info": {"pay_type": {"id": 2}},
                   "compensation_history": {"compensations": [{"id": None, "amount": 0.0}]}}
        before = copy.deepcopy(payload)
        UKGReadyEmployeeInput.validate_response(payload)
        UKGReadyEmployeeInput.validate_response({"employees": [payload]})
        self.assertEqual(payload, before)
        for supplement in [{"pay_info": {"pay_type": {}}},
                           {"compensation_history": {}},
                           {"compensation_history": {"compensations": [{"id": 2, "amount": []}]}}]:
            with self.subTest(supplement=supplement), self.assertRaises(ValidationError):
                UKGReadyEmployeeInput.validate_response({"id": 1, **supplement})

    def test_optional_supplements(self):
        UKGReadyEmployeeInput.validate_response({"id": None, "pay_info": None, "compensation_history": None})

