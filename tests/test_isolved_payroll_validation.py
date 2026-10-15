"""isolved payroll and paycheck validation and mapping integration."""
import copy
import unittest
from normalization.adapters import isolved


class IsolvedPayrollChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = isolved.normalize("payroll", payload, {})
        self.assertEqual(result["provider"], 'isolved')
        self.assertEqual(payload, before)

    def test_native_run_arrays_and_paged_checks(self):
        self.assert_valid([{"id": 1, "runNumber": 1}, {"id": None}])
        self.assert_valid({"results": [{"id": 10, "checkNumber": 1, "netPay": 0.0}],
                           "totalItems": 1, "totalPages": 1.0, "nextPageUrl": None})

    def test_combined_runs_and_nested_paycheck_records(self):
        payload = {
            "payroll_runs": [{"id": 1, "runNumber": 1}],
            "paychecks": [{"id": 10, "payrollRunNumber": 1, "grossPay": 0.0,
                           "earnings": [{"id": 2, "checkHours": 0.0}],
                           "deductions": [{"id": None, "checkDollars": 0.0}],
                           "directDeposits": [{"id": 3, "account": "0001", "depositAmount": 0.0}]}],
        }
        self.assert_valid(payload)
        payload["results"] = [{"id": None, "netPay": 0.0}]
        self.assert_valid(payload)

    def test_empty_and_nullable_sections(self):
        for payload in [[], {}, {"results": None}, {"results": []},
                        {"payroll_runs": None, "paychecks": None},
                        {"payroll_runs": [], "paychecks": []}]:
            with self.subTest(payload=payload):
                self.assertFalse(any(isolved.normalize("payroll", payload, {})[key]
                                     for key in ("payroll_runs", "paycheck_headers", "paychecks")))

    def test_run_ids_required_and_supplied_types_checked(self):
        for payload in [None, "wrong", [{}], {"payroll_runs": [{}]},
                        {"payroll_runs": "wrong"}, {"paychecks": "wrong"},
                        {"results": [{"id": 10, "netPay": []}]}, {"totalItems": []}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                isolved.normalize("payroll", payload, {})

    def test_invalid_supplemental_data_is_not_hidden_by_valid_runs(self):
        for field, bad in [("earnings", [{}]), ("directDeposits", [{"id": 1, "depositAmount": []}]),
                           ("deductions", [{"id": 1, "checkDollars": []}]),
                           ("taxes", [{}])]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                isolved.normalize("payroll", {"payroll_runs": [{"id": 1}],
                                              "paychecks": [{"id": 10, field: bad}]}, {})
        with self.assertRaises(ValueError):
            isolved.normalize("payroll", {"paychecks": [{"netPay": 0}], "results": "wrong"}, {})

    def test_optional_paycheck_sections_and_compatibility_imports(self):
        self.assert_valid({"paychecks": [{"id": 10, "earnings": None, "directDeposits": []}]})
        from normalization.source_models.isolved.isolved_source_model_paycheck import IsolvedCheckModel
        from normalization.source_models.isolved.isolved_source_model_payroll_run import IsolvedCheckModel as PayrollCheck
        self.assertIs(IsolvedCheckModel, PayrollCheck)


if __name__ == "__main__":
    unittest.main()
