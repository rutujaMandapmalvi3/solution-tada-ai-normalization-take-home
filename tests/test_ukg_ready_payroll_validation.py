"""UKG Ready payroll validation and mapping integration."""
import copy
import unittest
from normalization.adapters import ukg_ready
from pydantic import ValidationError
from normalization.source_models.ukg_ready.ukg_ready_source_model_payroll_run import UKGReadyPayrollInput


class UKGReadyPayrollValidationChecks(unittest.TestCase):
    def assert_valid(self, entity, payload):
        before = copy.deepcopy(payload)
        result = ukg_ready.normalize(entity, payload, {})
        self.assertEqual(result["provider"], "ukg-ready")
        self.assertEqual(payload, before)

    def test_payroll_all_sections_and_native_wrappers(self):
        self.assert_valid("payroll", {"payroll_runs": {"payrolls": [{"id": 1}]},
                                     "paycheck_list": {"pay_statements": [{"id": 2}]},
                                     "paychecks": [{"id": None, "earnings": [{"id": 3, "hours": 0}]}]})
        self.assert_valid("payroll", {"payrolls": [{"id": 1}], "pay_statements": [{"id": 2}]})
        self.assert_valid("payroll", {"id": 1, "payments": []})
        for payload in [{}, {"payroll_runs": None}, {"payrolls": []},
                        {"pay_statements": []}, {"paychecks": []}]:
            self.assertFalse(any(ukg_ready.normalize("payroll", payload, {})[key]
                                     for key in ("payroll_runs", "paycheck_headers", "paychecks")))
        for payload in [{"payroll_runs": {}}, {"paycheck_list": {}}, {"paychecks": [{}]},
                        {"payrolls": [{}]}, {"pay_statements": [{"id": None}]},
                        {"payroll_runs": {"payrolls": [{"id": 1}]},
                         "paychecks": [{"id": 2, "earnings": [{"id": 3, "hours": []}]}]}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                ukg_ready.normalize("payroll", payload, {})

    def test_payroll_combines_runs_headers_and_details(self):
        payload = {"payroll_runs": {"payrolls": [{"id": 1}]},
                   "paycheck_list": {"pay_statements": [{"id": 2}]},
                   "paychecks": [{"id": None, "earnings": [{"id": 3, "hours": 0}]}]}
        before = copy.deepcopy(payload)
        UKGReadyPayrollInput.validate_response(payload)
        UKGReadyPayrollInput.validate_response({"payrolls": [{"id": 1}], "pay_statements": [{"id": 2}]})
        UKGReadyPayrollInput.validate_response({"id": 2, "earnings": []})
        self.assertEqual(payload, before)
        for bad in [{"payroll_runs": {}}, {"paycheck_list": {}}, {"paychecks": [{}]},
                    {"paychecks": [{"id": 2, "earnings": [{"id": 3, "hours": []}]}]}]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                UKGReadyPayrollInput.validate_response(bad)

    def test_optional_supplements_and_conflicting_representations(self):
        UKGReadyPayrollInput.validate_response({"payroll_runs": None, "paycheck_list": None, "paychecks": None})
        payload = {"payroll_runs": {}, "payrolls": []}
        with self.subTest(payload=payload), self.assertRaises(ValueError):
            UKGReadyPayrollInput.validate_response(payload)

